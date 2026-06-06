import json
from datetime import date, datetime, time


def _json_default(value):
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=_json_default)}\n\n"


def chunk_text(text: str, size: int = 36) -> list[str]:
    if not text:
        return []
    return [text[i:i + size] for i in range(0, len(text), size)]
