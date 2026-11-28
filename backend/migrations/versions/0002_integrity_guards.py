"""Enforce review/final-category consistency and a single active model.

Revision ID: 0002_integrity_guards
Revises: 0001_initial_schema
"""
from alembic import op

revision = "0002_integrity_guards"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # A reviewer must be an active staff account, not a citizen.
    op.execute("""
    CREATE FUNCTION stnlp_guard_prediction_review_actor()
    RETURNS trigger AS $$
    DECLARE
        reviewer_roles jsonb;
        reviewer_status varchar(30);
    BEGIN
        SELECT role_codes, account_status
        INTO reviewer_roles, reviewer_status
        FROM users
        WHERE id = NEW.reviewer_id
        FOR KEY SHARE;

        IF NOT FOUND
           OR reviewer_status <> 'ACTIVE'
           OR NOT (reviewer_roles ?| ARRAY['RECEIVER', 'ADMIN']) THEN
            RAISE EXCEPTION 'Only an active RECEIVER or ADMIN may create a prediction review'
                USING ERRCODE = '42501';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_prediction_reviews_authorized_actor
    BEFORE INSERT ON prediction_reviews
    FOR EACH ROW EXECUTE FUNCTION stnlp_guard_prediction_review_actor();
    """)

    # The report update must be backed by a review inserted by this transaction.
    # xmin identifies rows created by the current PostgreSQL transaction.
    op.execute("""
    CREATE FUNCTION stnlp_guard_report_final_category()
    RETURNS trigger AS $$
    BEGIN
        IF NEW.final_category_id IS DISTINCT FROM OLD.final_category_id THEN
            IF NEW.final_category_id IS NULL OR NOT EXISTS (
                SELECT 1
                FROM prediction_reviews AS review_row
                WHERE review_row.report_id = NEW.id
                  AND review_row.selected_category_id = NEW.final_category_id
                  AND review_row.xmin::text = ((pg_current_xact_id()::text::numeric % 4294967296)::bigint)::text
            ) THEN
                RAISE EXCEPTION 'reports.final_category_id may only change with a matching review in the same transaction'
                    USING ERRCODE = '23514';
            END IF;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_reports_final_category_requires_review
    BEFORE UPDATE OF final_category_id ON reports
    FOR EACH ROW EXECUTE FUNCTION stnlp_guard_report_final_category();
    """)

    # Also reject a review-only write: at commit, its selected category must be
    # the report's current final category. This is deferred so the API can
    # insert the review and update the report in one transaction.
    op.execute("""
    CREATE FUNCTION stnlp_require_reviewed_final_category()
    RETURNS trigger AS $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM reports
            WHERE id = NEW.report_id
              AND final_category_id = NEW.selected_category_id
        ) THEN
            RAISE EXCEPTION 'A prediction review must update reports.final_category_id in the same transaction'
                USING ERRCODE = '23514';
        END IF;
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE CONSTRAINT TRIGGER trg_prediction_review_requires_final_category
    AFTER INSERT ON prediction_reviews
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW EXECUTE FUNCTION stnlp_require_reviewed_final_category();
    """)

    # A partial unique index is the database-level backstop for concurrent
    # activations, including the case where the active set was initially empty.
    op.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS uq_model_versions_single_active
    ON model_versions (model_status)
    WHERE model_status = 'ACTIVE';
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_prediction_review_requires_final_category ON prediction_reviews")
    op.execute("DROP FUNCTION IF EXISTS stnlp_require_reviewed_final_category()")
    op.execute("DROP TRIGGER IF EXISTS trg_reports_final_category_requires_review ON reports")
    op.execute("DROP FUNCTION IF EXISTS stnlp_guard_report_final_category()")
    op.execute("DROP TRIGGER IF EXISTS trg_prediction_reviews_authorized_actor ON prediction_reviews")
    op.execute("DROP FUNCTION IF EXISTS stnlp_guard_prediction_review_actor()")
    op.execute("DROP INDEX IF EXISTS uq_model_versions_single_active")
