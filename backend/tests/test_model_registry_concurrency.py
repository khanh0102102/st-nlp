from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.api.models as model_api
from app.db.models import ModelVersion, User
from app.infrastructure.database import SessionLocal


def _model(
    family: str,
    label: str,
    artifact_uri: str,
    checksum: str,
    *,
    status: str,
    admin_id=None,
) -> ModelVersion:
    return ModelVersion(
        model_family=family,
        algorithm_name=f"{family} test model",
        version_label=label,
        text_representation="tfidf-word-ngram",
        preprocessing_version="vi-nfc-lower-underthesea-v1",
        label_schema_version="stnlp-11-categories-v1",
        artifact_uri=artifact_uri,
        artifact_checksum=checksum,
        model_status=status,
        registered_by=admin_id,
        approved_by=admin_id if status in {"APPROVED", "ACTIVE"} else None,
        approved_at=datetime.now(UTC) if status in {"APPROVED", "ACTIVE"} else None,
    )


def test_database_partial_unique_index_rejects_two_active_models() -> None:
    admin_id = uuid4()
    first_id = uuid4()
    second_id = uuid4()

    with pytest.raises(IntegrityError):
        with SessionLocal.begin() as session:
            admin = User(
                id=admin_id,
                email=f"registry-index-{uuid4().hex}@example.test",
                role_codes=["ADMIN"],
            )
            session.add(admin)
            session.flush()
            session.add_all(
                [
                    _model("NB", "active-a", "a.bin", "a" * 64, status="ACTIVE", admin_id=admin_id),
                    _model("SVM", "active-b", "b.bin", "b" * 64, status="ACTIVE", admin_id=admin_id),
                ]
            )
            session.flush()


def test_concurrent_model_activation_keeps_exactly_one_active(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_a = tmp_path / "model-a.bin"
    artifact_b = tmp_path / "model-b.bin"
    artifact_a.write_bytes(b"model-a-artifact")
    artifact_b.write_bytes(b"model-b-artifact")
    checksum_a = hashlib.sha256(artifact_a.read_bytes()).hexdigest()
    checksum_b = hashlib.sha256(artifact_b.read_bytes()).hexdigest()

    admin_id = uuid4()
    model_a_id = uuid4()
    model_b_id = uuid4()
    email = f"registry-race-{uuid4().hex}@example.test"

    with SessionLocal.begin() as seed:
        admin = User(
            id=admin_id,
            email=email,
            display_name="Registry concurrency test",
            role_codes=["ADMIN"],
        )
        seed.add(admin)
        seed.flush()
        model_a = _model("NB", "race-a", "model-a.bin", checksum_a, status="APPROVED", admin_id=admin_id)
        model_a.id = model_a_id
        model_b = _model("SVM", "race-b", "model-b.bin", checksum_b, status="APPROVED", admin_id=admin_id)
        model_b.id = model_b_id
        seed.add_all([model_a, model_b])

    monkeypatch.setattr(
        model_api,
        "get_settings",
        lambda: SimpleNamespace(model_artifacts_dir=tmp_path),
    )
    monkeypatch.setattr(model_api, "_audit", lambda *args, **kwargs: True)

    barrier = Barrier(2)
    staff = SimpleNamespace(id=admin_id)

    def activate(model_id):
        with SessionLocal() as session:
            barrier.wait(timeout=10)
            return model_api.activate_model(
                model_id,
                SimpleNamespace(state=SimpleNamespace(request_id="registry-race-test")),
                session,
                staff,
            )

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(activate, model_a_id),
                executor.submit(activate, model_b_id),
            ]
            results = [future.result(timeout=30) for future in futures]

        assert len(results) == 2
        with SessionLocal() as check:
            rows = check.scalars(
                select(ModelVersion).where(
                    ModelVersion.id.in_([model_a_id, model_b_id])
                )
            ).all()
            assert len(rows) == 2
            assert sum(row.model_status == "ACTIVE" for row in rows) == 1
            assert sum(row.model_status == "RETIRED" for row in rows) == 1
    finally:
        with SessionLocal.begin() as cleanup:
            cleanup.execute(
                delete(ModelVersion).where(
                    ModelVersion.id.in_([model_a_id, model_b_id])
                )
            )
            cleanup.execute(delete(User).where(User.id == admin_id))



def test_rollback_reactivates_approved_model_and_records_lifecycle_audit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    active_artifact = tmp_path / "current-active.bin"
    rollback_artifact = tmp_path / "previous-approved.bin"
    active_artifact.write_bytes(b"current-active-artifact")
    rollback_artifact.write_bytes(b"previous-approved-artifact")
    active_checksum = hashlib.sha256(active_artifact.read_bytes()).hexdigest()
    rollback_checksum = hashlib.sha256(rollback_artifact.read_bytes()).hexdigest()

    admin_id = uuid4()
    active_id = uuid4()
    rollback_id = uuid4()
    now = datetime.now(UTC)

    with SessionLocal.begin() as seed:
        admin = User(
            id=admin_id,
            email=f"registry-rollback-{uuid4().hex}@example.test",
            display_name="Registry rollback test",
            role_codes=["ADMIN"],
        )
        seed.add(admin)
        seed.flush()

        active_model = _model(
            "SVM",
            "current-active",
            "current-active.bin",
            active_checksum,
            status="ACTIVE",
            admin_id=admin_id,
        )
        active_model.id = active_id
        active_model.activated_at = now

        rollback_model = _model(
            "NB",
            "previous-approved",
            "previous-approved.bin",
            rollback_checksum,
            status="RETIRED",
            admin_id=admin_id,
        )
        rollback_model.id = rollback_id
        rollback_model.approved_by = admin_id
        rollback_model.approved_at = now
        rollback_model.activated_at = now
        rollback_model.retired_at = now

        seed.add_all([active_model, rollback_model])

    monkeypatch.setattr(
        model_api,
        "get_settings",
        lambda: SimpleNamespace(model_artifacts_dir=tmp_path),
    )
    audited_actions: list[str] = []

    def record_audit(*args, **kwargs) -> bool:
        audited_actions.append(args[2])
        return True

    monkeypatch.setattr(model_api, "_audit", record_audit)

    request = SimpleNamespace(
        state=SimpleNamespace(request_id="registry-rollback-test")
    )
    staff = SimpleNamespace(id=admin_id)

    try:
        with SessionLocal() as session:
            response = model_api.rollback_model(
                rollback_id,
                request,
                session,
                staff,
            )

        assert response["data"]["status"] == "ACTIVE"
        assert response["meta"]["audit_event_recorded"] is True
        assert audited_actions == ["model.rolled_back"]

        with SessionLocal() as check:
            current = check.get(ModelVersion, active_id)
            restored = check.get(ModelVersion, rollback_id)
            assert current is not None
            assert restored is not None
            assert current.model_status == "RETIRED"
            assert current.retired_at is not None
            assert restored.model_status == "ACTIVE"
            assert restored.activated_at is not None
            assert restored.retired_at is None
            assert restored.approved_at == now
            assert restored.approved_by == admin_id
            assert check.scalar(
                select(ModelVersion.id).where(ModelVersion.model_status == "ACTIVE")
            ) == rollback_id
    finally:
        with SessionLocal.begin() as cleanup:
            cleanup.execute(
                delete(ModelVersion).where(
                    ModelVersion.id.in_([active_id, rollback_id])
                )
            )
            cleanup.execute(delete(User).where(User.id == admin_id))
