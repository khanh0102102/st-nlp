from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAtMixin, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "account_status IN ('ACTIVE', 'SUSPENDED', 'DISABLED')",
            name="account_status_allowed",
        ),
        CheckConstraint(
            "jsonb_typeof(role_codes) = 'array' AND "
            "role_codes <@ '[\"CITIZEN\", \"RECEIVER\", \"ADMIN\"]'::jsonb",
            name="role_codes_allowlist",
        ),
        CheckConstraint(
            "(auth_provider IS NULL AND provider_subject IS NULL) OR "
            "(auth_provider IS NOT NULL AND provider_subject IS NOT NULL)",
            name="auth_identity_pair",
        ),
        Index(
            "uq_users_auth_provider_subject",
            "auth_provider",
            "provider_subject",
            unique=True,
            postgresql_where=text(
                "auth_provider IS NOT NULL AND provider_subject IS NOT NULL"
            ),
        ),
        Index("ix_users_email", "email"),
    )

    auth_provider: Mapped[str | None] = mapped_column(String(30))
    provider_subject: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(320))
    display_name: Mapped[str | None] = mapped_column(String(150))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    password_hash: Mapped[str | None] = mapped_column(Text)
    role_codes: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: ["CITIZEN"],
        server_default=text("""'["CITIZEN"]'::jsonb"""),
    )
    account_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="ACTIVE", server_default=text("'ACTIVE'")
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IncidentCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "incident_categories"
    __table_args__ = (
        CheckConstraint("sort_order BETWEEN 1 AND 11", name="sort_order_range"),
    )

    category_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    category_name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )


class Report(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reports"
    __table_args__ = (
        CheckConstraint(
            "length(btrim(raw_content)) > 0", name="raw_content_nonempty"
        ),
        CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude IS NOT NULL AND longitude IS NOT NULL)",
            name="coordinates_pair",
        ),
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="latitude_range",
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="longitude_range",
        ),
        CheckConstraint(
            "status IN ('SUBMITTED', 'UNDER_REVIEW', 'IN_PROGRESS', "
            "'RESOLVED', 'REJECTED', 'CLOSED')",
            name="status_allowed",
        ),
        Index("ix_reports_user_created", "user_id", "created_at"),
        Index("ix_reports_status_created", "status", "created_at"),
        Index("ix_reports_final_category_created", "final_category_id", "created_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", name="fk_reports_user_id_users"), nullable=False
    )
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    final_category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "incident_categories.id",
            name="fk_reports_final_category_id_incident_categories",
        )
    )
    status: Mapped[str] = mapped_column(
        String(40), nullable=False, default="SUBMITTED", server_default=text("'SUBMITTED'")
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ReportAttachment(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "report_attachments"
    __table_args__ = (
        CheckConstraint("file_size_bytes > 0", name="file_size_positive"),
        CheckConstraint(
            "verified_mime_type IN ('image/jpeg', 'image/png', 'image/webp')",
            name="mime_type_allowed",
        ),
        CheckConstraint(
            "upload_status IN ('PENDING', 'READY', 'FAILED', 'QUARANTINED')",
            name="upload_status_allowed",
        ),
        Index("ix_report_attachments_report_id", "report_id"),
    )

    report_id: Mapped[UUID] = mapped_column(
        ForeignKey("reports.id", name="fk_report_attachments_report_id_reports"),
        nullable=False,
    )
    uploaded_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", name="fk_report_attachments_uploaded_by_users")
    )
    storage_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    original_filename: Mapped[str | None] = mapped_column(String(255))
    verified_mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64))
    upload_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="PENDING", server_default=text("'PENDING'")
    )


class PreprocessingRun(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "preprocessing_runs"
    __table_args__ = (
        UniqueConstraint("id", "report_id", name="uq_preprocessing_runs_id_report"),
        CheckConstraint(
            "processing_status IN ('SUCCEEDED', 'FAILED', 'SKIPPED')",
            name="processing_status_allowed",
        ),
        CheckConstraint(
            "processing_time_ms IS NULL OR processing_time_ms >= 0",
            name="processing_time_nonnegative",
        ),
        CheckConstraint(
            "NOT (processed_text IS NOT NULL AND processed_artifact_key IS NOT NULL)",
            name="processed_output_exclusive",
        ),
        Index("ix_preprocessing_runs_report_created", "report_id", "created_at"),
        Index("ix_preprocessing_runs_version", "preprocessing_version"),
        Index("ix_preprocessing_runs_fingerprint", "input_fingerprint"),
    )

    report_id: Mapped[UUID] = mapped_column(
        ForeignKey("reports.id", name="fk_preprocessing_runs_report_id_reports"),
        nullable=False,
    )
    preprocessing_version: Mapped[str] = mapped_column(String(80), nullable=False)
    pipeline_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tokenizer_name: Mapped[str | None] = mapped_column(String(100))
    tokenizer_version: Mapped[str | None] = mapped_column(String(80))
    normalization_config_json: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    stopword_config_json: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    processed_text: Mapped[str | None] = mapped_column(Text)
    processed_artifact_key: Mapped[str | None] = mapped_column(Text)
    input_fingerprint: Mapped[str | None] = mapped_column(String(64))
    processing_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="SUCCEEDED"
    )
    error_code: Mapped[str | None] = mapped_column(String(80))
    processing_time_ms: Mapped[int | None] = mapped_column(BigInteger)


class Dataset(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "datasets"
    __table_args__ = (
        UniqueConstraint(
            "dataset_name", "version_label", name="uq_datasets_name_version"
        ),
        CheckConstraint(
            "dataset_status IN ('DRAFT', 'VALIDATING', 'READY', 'FROZEN', 'ARCHIVED')",
            name="dataset_status_allowed",
        ),
        CheckConstraint("sample_count >= 0", name="sample_count_nonnegative"),
        Index("ix_datasets_status", "dataset_status"),
    )

    dataset_name: Mapped[str] = mapped_column(String(150), nullable=False)
    version_label: Mapped[str] = mapped_column(String(60), nullable=False)
    parent_dataset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("datasets.id", name="fk_datasets_parent_dataset_id_datasets")
    )
    dataset_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="DRAFT", server_default=text("'DRAFT'")
    )
    label_schema_version: Mapped[str] = mapped_column(String(40), nullable=False)
    split_config_json: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    sample_count: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default=text("0")
    )
    class_distribution_json: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    validation_report_uri: Mapped[str | None] = mapped_column(Text)
    provenance_summary: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", name="fk_datasets_created_by_users"), nullable=False
    )
    frozen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TrainingRun(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "training_runs"
    __table_args__ = (
        CheckConstraint(
            "model_family IN ('NB', 'SVM', 'CNN_1D', 'LSTM')",
            name="model_family_allowed",
        ),
        CheckConstraint(
            "run_status IN ('QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELLED')",
            name="run_status_allowed",
        ),
        CheckConstraint(
            "duration_ms IS NULL OR duration_ms >= 0",
            name="duration_nonnegative",
        ),
        Index("ix_training_runs_dataset_created", "dataset_id", "created_at"),
        Index("ix_training_runs_status", "run_status"),
    )

    dataset_id: Mapped[UUID] = mapped_column(
        ForeignKey("datasets.id", name="fk_training_runs_dataset_id_datasets"),
        nullable=False,
    )
    model_family: Mapped[str] = mapped_column(String(40), nullable=False)
    algorithm_name: Mapped[str] = mapped_column(String(100), nullable=False)
    text_representation: Mapped[str] = mapped_column(String(80), nullable=False)
    hyperparameters_json: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    imbalance_strategy: Mapped[str | None] = mapped_column(String(80))
    preprocessing_version: Mapped[str] = mapped_column(String(80), nullable=False)
    random_seed: Mapped[int | None] = mapped_column(BigInteger)
    code_version: Mapped[str | None] = mapped_column(String(80))
    environment_version: Mapped[str | None] = mapped_column(String(120))
    run_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="QUEUED", server_default=text("'QUEUED'")
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(BigInteger)
    output_artifact_uri: Mapped[str | None] = mapped_column(Text)
    failure_summary: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", name="fk_training_runs_created_by_users"),
        nullable=False,
    )


class ModelVersion(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "model_versions"
    __table_args__ = (
        UniqueConstraint(
            "model_family", "version_label", name="uq_model_versions_family_version"
        ),
        CheckConstraint(
            "model_family IN ('NB', 'SVM', 'CNN_1D', 'LSTM')",
            name="model_family_allowed",
        ),
        CheckConstraint(
            "model_status IN ('REGISTERED', 'EVALUATED', 'APPROVED', "
            "'ACTIVE', 'RETIRED', 'REJECTED')",
            name="model_status_allowed",
        ),
        Index("ix_model_versions_training_run", "training_run_id"),
        Index(
            "uq_model_versions_single_active",
            "model_status",
            unique=True,
            postgresql_where=text("model_status = 'ACTIVE'"),
        ),
    )

    model_family: Mapped[str] = mapped_column(String(40), nullable=False)
    algorithm_name: Mapped[str] = mapped_column(String(100), nullable=False)
    version_label: Mapped[str] = mapped_column(String(80), nullable=False)
    text_representation: Mapped[str] = mapped_column(String(80), nullable=False)
    preprocessing_version: Mapped[str] = mapped_column(String(80), nullable=False)
    label_schema_version: Mapped[str] = mapped_column(String(40), nullable=False)
    training_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("training_runs.id", name="fk_model_versions_training_run_id_training_runs")
    )
    artifact_uri: Mapped[str] = mapped_column(Text, nullable=False)
    artifact_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    hyperparameters_json: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    metrics_summary_json: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    model_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="REGISTERED",
        server_default=text("'REGISTERED'")
    )
    registered_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", name="fk_model_versions_registered_by_users")
    )
    approved_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", name="fk_model_versions_approved_by_users")
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Prediction(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "predictions"
    __table_args__ = (
        UniqueConstraint("id", "report_id", name="uq_predictions_id_report"),
        ForeignKeyConstraint(
            ["preprocessing_run_id", "report_id"],
            ["preprocessing_runs.id", "preprocessing_runs.report_id"],
            name="fk_predictions_preprocessing_report",
        ),
        CheckConstraint(
            "inference_status IN ('PENDING', 'SUCCEEDED', 'INSUFFICIENT_INFORMATION', "
            "'INVALID_INPUT', 'INFERENCE_FAILED')",
            name="inference_status_allowed",
        ),
        CheckConstraint(
            "confidence_type IS NULL OR confidence_type IN "
            "('RAW_DECISION_SCORE', 'MODEL_PROBABILITY_UNCALIBRATED', "
            "'CALIBRATED_PROBABILITY')",
            name="confidence_type_allowed",
        ),
        CheckConstraint(
            "confidence_value IS NULL OR confidence_type IS NOT NULL",
            name="confidence_type_required",
        ),
        CheckConstraint(
            "confidence_value IS NULL OR "
            "(confidence_value > '-Infinity'::numeric AND "
            "confidence_value < 'Infinity'::numeric AND "
            "(confidence_type = 'RAW_DECISION_SCORE' OR "
            "confidence_value BETWEEN 0 AND 1))",
            name="confidence_value_valid",
        ),
        CheckConstraint(
            "(inference_status = 'SUCCEEDED' AND model_version_id IS NOT NULL "
            "AND predicted_category_id IS NOT NULL) OR "
            "(inference_status <> 'SUCCEEDED' AND predicted_category_id IS NULL)",
            name="success_requires_category_and_model",
        ),
        CheckConstraint(
            "processing_time_ms IS NULL OR processing_time_ms >= 0",
            name="processing_time_nonnegative",
        ),
        Index("ix_predictions_report_created", "report_id", "created_at"),
        Index("ix_predictions_model_version", "model_version_id"),
        Index("ix_predictions_category", "predicted_category_id"),
        Index("ix_predictions_status", "inference_status"),
    )

    report_id: Mapped[UUID] = mapped_column(
        ForeignKey("reports.id", name="fk_predictions_report_id_reports"),
        nullable=False,
    )
    preprocessing_run_id: Mapped[UUID] = mapped_column(
        nullable=False
    )
    model_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("model_versions.id", name="fk_predictions_model_version_id_model_versions")
    )
    predicted_category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "incident_categories.id",
            name="fk_predictions_predicted_category_id_incident_categories",
        )
    )
    confidence_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 10))
    confidence_type: Mapped[str | None] = mapped_column(String(40))
    needs_review: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    inference_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="PENDING", server_default=text("'PENDING'")
    )
    error_code: Mapped[str | None] = mapped_column(String(80))
    processing_time_ms: Mapped[int | None] = mapped_column(BigInteger)


class PredictionReview(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "prediction_reviews"
    __table_args__ = (
        UniqueConstraint("id", "report_id", name="uq_prediction_reviews_id_report"),
        ForeignKeyConstraint(
            ["prediction_id", "report_id"],
            ["predictions.id", "predictions.report_id"],
            name="fk_prediction_reviews_prediction_report",
        ),
        CheckConstraint(
            "action_code IN ('CONFIRMED', 'CORRECTED')",
            name="action_code_allowed",
        ),
        Index("ix_prediction_reviews_report_reviewed", "report_id", "reviewed_at"),
        Index("ix_prediction_reviews_prediction_reviewed", "prediction_id", "reviewed_at"),
        Index("ix_prediction_reviews_reviewer_reviewed", "reviewer_id", "reviewed_at"),
    )

    report_id: Mapped[UUID] = mapped_column(
        ForeignKey("reports.id", name="fk_prediction_reviews_report_id_reports"),
        nullable=False,
    )
    prediction_id: Mapped[UUID] = mapped_column(nullable=False)
    reviewer_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", name="fk_prediction_reviews_reviewer_id_users"),
        nullable=False,
    )
    previous_category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "incident_categories.id",
            name="fk_prediction_reviews_previous_category_id_incident_categories",
        )
    )
    selected_category_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "incident_categories.id",
            name="fk_prediction_reviews_selected_category_id_incident_categories",
        ),
        nullable=False,
    )
    action_code: Mapped[str] = mapped_column(String(30), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    request_version: Mapped[int | None] = mapped_column(Integer)


class DatasetSample(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "dataset_samples"
    __table_args__ = (
        ForeignKeyConstraint(
            ["source_review_id", "source_report_id"],
            ["prediction_reviews.id", "prediction_reviews.report_id"],
            name="fk_dataset_samples_source_review_report",
        ),
        CheckConstraint(
            "labeling_status IN ('LABELED', 'UNLABELED', 'NEEDS_REVIEW', "
            "'INSUFFICIENT_INFORMATION')",
            name="labeling_status_allowed",
        ),
        CheckConstraint(
            "(category_id IS NOT NULL AND labeling_status = 'LABELED') OR "
            "(category_id IS NULL AND labeling_status IN "
            "('UNLABELED', 'NEEDS_REVIEW', 'INSUFFICIENT_INFORMATION'))",
            name="category_matches_label_status",
        ),
        CheckConstraint(
            "split IS NULL OR split IN ('TRAIN', 'VALIDATION', 'TEST')",
            name="split_allowed",
        ),
        CheckConstraint(
            "source_review_id IS NULL OR source_report_id IS NOT NULL",
            name="source_review_requires_report",
        ),
        Index("ix_dataset_samples_dataset_split", "dataset_id", "split"),
        Index("ix_dataset_samples_dataset_category", "dataset_id", "category_id"),
        Index("ix_dataset_samples_source_report", "source_report_id"),
        Index("ix_dataset_samples_fingerprint", "text_fingerprint"),
    )

    dataset_id: Mapped[UUID] = mapped_column(
        ForeignKey("datasets.id", name="fk_dataset_samples_dataset_id_datasets"),
        nullable=False,
    )
    text_content: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "incident_categories.id",
            name="fk_dataset_samples_category_id_incident_categories",
        )
    )
    labeling_status: Mapped[str] = mapped_column(String(40), nullable=False)
    split: Mapped[str | None] = mapped_column(String(20))
    source_type: Mapped[str] = mapped_column(String(40), nullable=False)
    source_report_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("reports.id", name="fk_dataset_samples_source_report_id_reports")
    )
    source_review_id: Mapped[UUID | None] = mapped_column(nullable=True)
    text_fingerprint: Mapped[str | None] = mapped_column(String(64))
    label_guideline_version: Mapped[str | None] = mapped_column(String(40))


class TrainingMetric(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "training_metrics"
    __table_args__ = (
        CheckConstraint(
            "metric_value > '-Infinity'::numeric AND metric_value < 'Infinity'::numeric",
            name="metric_value_finite",
        ),
        CheckConstraint(
            "data_split IN ('TRAIN', 'VALIDATION', 'TEST')",
            name="data_split_allowed",
        ),
        CheckConstraint(
            "averaging IS NULL OR averaging IN ('MACRO', 'WEIGHTED', 'MICRO')",
            name="averaging_allowed",
        ),
        CheckConstraint(
            "support_count IS NULL OR support_count >= 0",
            name="support_count_nonnegative",
        ),
        CheckConstraint(
            "epoch_or_step IS NULL OR epoch_or_step >= 0",
            name="epoch_or_step_nonnegative",
        ),
        Index("ix_training_metrics_run_name_split", "training_run_id", "metric_name", "data_split"),
        Index("ix_training_metrics_category", "category_id"),
    )

    training_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("training_runs.id", name="fk_training_metrics_training_run_id_training_runs"),
        nullable=False,
    )
    metric_name: Mapped[str] = mapped_column(String(60), nullable=False)
    metric_value: Mapped[Decimal] = mapped_column(Numeric(16, 10), nullable=False)
    data_split: Mapped[str] = mapped_column(String(20), nullable=False)
    averaging: Mapped[str | None] = mapped_column(String(20))
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "incident_categories.id",
            name="fk_training_metrics_category_id_incident_categories",
        )
    )
    support_count: Mapped[int | None] = mapped_column(BigInteger)
    epoch_or_step: Mapped[int | None] = mapped_column(Integer)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    metric_details_json: Mapped[dict[str, object] | None] = mapped_column(JSONB)
