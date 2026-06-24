import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ_TAIPEI = timezone(timedelta(hours=8))
SENT_FILE = Path("sent_links.json")


def load() -> dict:
    if SENT_FILE.exists():
        try:
            return json.loads(SENT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save(sent: dict):
    cutoff  = (datetime.now(TZ_TAIPEI) - timedelta(hours=48)).isoformat()
    cleaned = {k: v for k, v in sent.items() if v >= cutoff}
    SENT_FILE.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")


def filter_new(items: list[dict], sent: dict) -> tuple[list[dict], dict]:
    now      = datetime.now(TZ_TAIPEI).isoformat()
    new_sent = {}
    result   = []
    for item in items:
        link = item.get("link", "")
        if link and link not in sent and link not in new_sent:
            result.append(item)
            new_sent[link] = now
    return result, new_sent
