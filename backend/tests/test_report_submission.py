from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

import app.api.reports as reports_module
from app.api.reports import ReportCreate, create_report
from app.db.models import Prediction, PreprocessingRun, Report


class RecordingSession:
    """Minimal session double for the report submission transaction boundary."""

    def __init__(self) -> None:
        self.records: list[object] = []
        self.committed = False

    def add(self, record: object) -> None:
        self.records.append(record)

    def flush(self) -> None:
        for record in self.records:
            if getattr(record, "id", None) is None:
                setattr(record, "id", uuid4())

    def commit(self) -> None:
        self.flush()
        self.committed = True

    def refresh(self, record: object) -> None:
        return None


def _request() -> SimpleNamespace:
    return SimpleNamespace(state=SimpleNamespace(request_id="report-test-request"))


def _citizen() -> SimpleNamespace:
    return SimpleNamespace(id=uuid4(), role_codes=["CITIZEN"])


def _patch_report_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> list[dict[str, object]]:
    audits: list[dict[str, object]] = []
    monkeypatch.setattr(
        reports_module,
        "get_settings",
        lambda: SimpleNamespace(ml_service_url=""),
    )
    monkeypatch.setattr(
        reports_module,
        "_report_payload",
        lambda report: {"id": str(report.id), "raw_content": report.raw_content},
    )

    def record_audit(*args, **kwargs) -> bool:
        audits.append(kwargs)
        return True

    monkeypatch.setattr(reports_module, "_audit", record_audit)
    return audits


def test_create_report_without_ml_service_keeps_report_and_records_audit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audits = _patch_report_dependencies(monkeypatch)
    session = RecordingSession()
    submitted_text = "  Đèn tín hiệu KHÔNG hoạt động tại ngã tư.  \n"

    result = create_report(
        ReportCreate(raw_content=submitted_text),
        _request(),
        session,  # type: ignore[arg-type]
        _citizen(),  # type: ignore[arg-type]
    )

    report = next(item for item in session.records if isinstance(item, Report))
    preprocessing = next(
        item for item in session.records if isinstance(item, PreprocessingRun)
    )
    prediction = next(
        item for item in session.records if isinstance(item, Prediction)
    )

    assert session.committed is True
    assert report.raw_content == submitted_text
    assert preprocessing.processing_status == "SKIPPED"
    assert prediction.inference_status == "INFERENCE_FAILED"
    assert prediction.predicted_category_id is None
    assert prediction.confidence_value is None
    assert prediction.confidence_type is None
    assert result["meta"]["prediction"]["inference_status"] == "INFERENCE_FAILED"
    assert result["meta"]["audit_event_recorded"] is True
    assert len(audits) == 1
    assert audits[0]["action"] == "report.submitted"
    assert audits[0]["details"]["inference_status"] == "INFERENCE_FAILED"


def test_create_report_rejects_whitespace_only_content_without_persisting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_report_dependencies(monkeypatch)
    session = RecordingSession()

    with pytest.raises(HTTPException) as error:
        create_report(
            ReportCreate(raw_content=" \n  \t"),
            _request(),
            session,  # type: ignore[arg-type]
            _citizen(),  # type: ignore[arg-type]
        )

    assert error.value.status_code == 422
    assert session.records == []
    assert session.committed is False



def test_database_rejects_mutation_of_original_report_content(
    db_session: Session,
) -> None:
    user = _citizen(db_session)
    report = Report(
        user_id=user.id,
        raw_content="  Nội dung gốc có dấu tiếng Việt.\\n",
    )
    db_session.add(report)
    db_session.flush()

    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.execute(
                update(Report)
                .where(Report.id == report.id)
                .values(raw_content="Nội dung đã bị thay đổi.")
            )

    db_session.refresh(report)
    assert report.raw_content == "  Nội dung gốc có dấu tiếng Việt.\\n"
