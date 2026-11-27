from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    app_name: str = "ST-NLP API"
    app_env: str = "development"
    secret_key: SecretStr = SecretStr(
        "local-only-change-before-any-shared-environment"
    )
    database_url: str = (
        "postgresql+psycopg://stnlp:stnlp_local_only_change_me@db:5432/stnlp"
    )
    cors_origins_csv: str = "http://localhost:8080"
    uploads_dir: Path = Path("/data/uploads")
    model_artifacts_dir: Path = Path("/data/model-artifacts")
    audit_log_path: Path = Path("/data/audit/audit-events.jsonl")
    google_client_id: str | None = None
    google_client_secret: SecretStr | None = None
    google_redirect_uri: str | None = None

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins_csv.split(",")
            if origin.strip()
        ]

    @property
    def google_oauth_enabled(self) -> bool:
        secret = (
            self.google_client_secret.get_secret_value()
            if self.google_client_secret is not None
            else ""
        )
        return bool(
            self.google_client_id
            and self.google_client_id.strip()
            and secret.strip()
            and self.google_redirect_uri
            and self.google_redirect_uri.strip()
        )

    @model_validator(mode="after")
    def reject_local_secret_outside_development(self) -> "Settings":
        local_secret = "local-only-change-before-any-shared-environment"
        if (
            self.app_env.lower() not in {"development", "test"}
            and self.secret_key.get_secret_value() == local_secret
        ):
            raise ValueError(
                "SECRET_KEY must be changed outside development/test environments"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
