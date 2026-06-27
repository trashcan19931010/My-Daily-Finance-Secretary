import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ   = timezone(timedelta(hours=8))
FILE = Path("sent_links.json")

def load():
    try:
        return json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}
    except Exception:
        return {}

def save(sent):
    cut = (datetime.now(TZ) - timedelta(hours=48)).isoformat()
    FILE.write_text(json.dumps({k: v for k, v in sent.items() if v >= cut}, ensure_ascii=False, indent=2), encoding="utf-8")

def filter_new(items, sent):
    now, new_sent, result = datetime.now(TZ).isoformat(), {}, []
    for item in items:
        lnk = item.get("link", "")
        if lnk and lnk not in sent and lnk not in new_sent:
            result.append(item)
            new_sent[lnk] = now
    return result, new_sent
