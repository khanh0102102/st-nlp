"""Create the ST-NLP 12-table relational baseline."""

from alembic import op

from app.db.base import Base
from app.db import models  # noqa: F401 - register all tables

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=False)

    op.execute("""
    CREATE FUNCTION stnlp_reject_immutable_row()
    RETURNS trigger AS $$
    BEGIN
        RAISE EXCEPTION 'ST-NLP table %.% is append-only', TG_TABLE_SCHEMA, TG_TABLE_NAME
            USING ERRCODE = '55000';
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_predictions_append_only
    BEFORE UPDATE OR DELETE ON predictions
    FOR EACH ROW EXECUTE FUNCTION stnlp_reject_immutable_row();
    """)
    op.execute("""
    CREATE TRIGGER trg_prediction_reviews_append_only
    BEFORE UPDATE OR DELETE ON prediction_reviews
    FOR EACH ROW EXECUTE FUNCTION stnlp_reject_immutable_row();
    """)

    op.execute("""
    CREATE FUNCTION stnlp_reject_raw_content_change()
    RETURNS trigger AS $$
    BEGIN
        IF NEW.raw_content IS DISTINCT FROM OLD.raw_content THEN
            RAISE EXCEPTION 'reports.raw_content is immutable'
                USING ERRCODE = '55000';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_reports_raw_content_immutable
    BEFORE UPDATE OF raw_content ON reports
    FOR EACH ROW EXECUTE FUNCTION stnlp_reject_raw_content_change();
    """)

    op.execute("""
    CREATE FUNCTION stnlp_guard_frozen_dataset()
    RETURNS trigger AS $$
    BEGIN
        IF OLD.dataset_status = 'FROZEN' THEN
            RAISE EXCEPTION 'Frozen dataset versions are immutable'
                USING ERRCODE = '55000';
        END IF;
        IF TG_OP = 'DELETE' THEN
            RETURN OLD;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_datasets_frozen_immutable
    BEFORE UPDATE OR DELETE ON datasets
    FOR EACH ROW EXECUTE FUNCTION stnlp_guard_frozen_dataset();
    """)

    op.execute("""
    CREATE FUNCTION stnlp_guard_dataset_sample()
    RETURNS trigger AS $$
    DECLARE
        target_status varchar(30);
    BEGIN
        IF TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
            SELECT dataset_status INTO target_status
            FROM datasets WHERE id = OLD.dataset_id;
            IF target_status = 'FROZEN' THEN
                RAISE EXCEPTION 'Samples in frozen dataset versions are immutable'
                    USING ERRCODE = '55000';
            END IF;
        END IF;

        IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
            SELECT dataset_status INTO target_status
            FROM datasets WHERE id = NEW.dataset_id;
            IF target_status = 'FROZEN' THEN
                RAISE EXCEPTION 'Samples in frozen dataset versions are immutable'
                    USING ERRCODE = '55000';
            END IF;
            RETURN NEW;
        END IF;
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_dataset_samples_frozen_immutable
    BEFORE INSERT OR UPDATE OR DELETE ON dataset_samples
    FOR EACH ROW EXECUTE FUNCTION stnlp_guard_dataset_sample();
    """)

    op.execute("""
    CREATE FUNCTION stnlp_require_frozen_training_dataset()
    RETURNS trigger AS $$
    DECLARE
        target_status varchar(30);
    BEGIN
        SELECT dataset_status INTO target_status
        FROM datasets WHERE id = NEW.dataset_id;
        IF target_status IS DISTINCT FROM 'FROZEN' THEN
            RAISE EXCEPTION 'Training runs require a FROZEN dataset version'
                USING ERRCODE = '23514';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_training_runs_require_frozen_dataset
    BEFORE INSERT OR UPDATE OF dataset_id ON training_runs
    FOR EACH ROW EXECUTE FUNCTION stnlp_require_frozen_training_dataset();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_training_runs_require_frozen_dataset ON training_runs")
    op.execute("DROP FUNCTION IF EXISTS stnlp_require_frozen_training_dataset()")
    op.execute("DROP TRIGGER IF EXISTS trg_dataset_samples_frozen_immutable ON dataset_samples")
    op.execute("DROP FUNCTION IF EXISTS stnlp_guard_dataset_sample()")
    op.execute("DROP TRIGGER IF EXISTS trg_datasets_frozen_immutable ON datasets")
    op.execute("DROP FUNCTION IF EXISTS stnlp_guard_frozen_dataset()")
    op.execute("DROP TRIGGER IF EXISTS trg_reports_raw_content_immutable ON reports")
    op.execute("DROP FUNCTION IF EXISTS stnlp_reject_raw_content_change()")
    op.execute("DROP TRIGGER IF EXISTS trg_prediction_reviews_append_only ON prediction_reviews")
    op.execute("DROP TRIGGER IF EXISTS trg_predictions_append_only ON predictions")
    op.execute("DROP FUNCTION IF EXISTS stnlp_reject_immutable_row()")
    Base.metadata.drop_all(bind=op.get_bind())
