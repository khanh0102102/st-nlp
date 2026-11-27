import json
import os
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import UUID

from app.core.config import get_settings

_write_lock = Lock()


def append_audit_event(
    *,
    actor_id: UUID | None,
    action: str,
    resource_type: str,
    resource_id: UUID | str,
    outcome: str,
    request_id: str | None,
    details: dict[str, Any] | None = None,
) -> None:
    """Append a minimal local audit event; never pass raw content or secrets."""
    payload = {
        "actor_id": str(actor_id) if actor_id else None,
        "action": action,
        "resource_type": resource_type,
        "resource_id": str(resource_id),
        "timestamp": datetime.now(UTC).isoformat(),
        "outcome": outcome,
        "request_id": request_id,
        "details": details or {},
    }
    encoded = (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    path = get_settings().audit_log_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with _write_lock:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            os.write(fd, encoded)
        finally:
            os.close(fd)


def read_resource_audit_events(
    *,
    resource_type: str,
    resource_id: UUID,
    limit: int = 100,
) -> list[dict[str, Any]]:
    path: Path = get_settings().audit_log_path
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("resource_type") == resource_type and event.get("resource_id") == str(resource_id):
                events.append(event)
    return events[-limit:]
