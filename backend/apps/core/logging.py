import json
import logging
from datetime import UTC, datetime


SAFE_EXTRA_FIELDS = (
    "event",
    "request_id",
    "method",
    "path",
    "status_code",
    "exception_type",
    "action",
)


class JsonFormatter(logging.Formatter):
    """Structured logs with an intentionally small, non-sensitive field allow-list."""

    def format(self, record):
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in SAFE_EXTRA_FIELDS:
            value = getattr(record, field, None)
            if value not in (None, ""):
                payload[field] = value
        return json.dumps(payload, ensure_ascii=False)
