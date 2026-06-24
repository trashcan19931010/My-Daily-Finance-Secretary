import os
import requests
from datetime import datetime, date, timezone, timedelta

TZ_TAIPEI = timezone(timedelta(hours=8))


def _fmt(ts_unix=None, ts_str=None) -> str:
    try:
        if ts_unix:
            dt = datetime.fromtimestamp(int(ts_unix), tz=timezone.utc)
        elif ts_str:
            ts_str = str(ts_str).strip()
            for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d%H%M%S",
                        "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z",
                        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%d %H:%M", "%Y%m%d"):
                try:
                    s  = ts_str.replace("Z", "+00:00")
                    dt = datetime.strptime(s, fmt)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    break
                except Exception:
                    continue
            else:
                return ""
        else:
            return ""
        return dt.astimezone(TZ_TAIPEI).strftime("%Y/%m/%d %H:%M")
    except Exception:
        return ""


def _safe_json(res: requests.Response, source: str):
    text = (res.text or "").strip()
    if not text:
        print(f"⚠️  {source}: 回應為空")
        return None
    if text.lower() in ("null", "none", "undefined"):
        print(f"⚠️  {source}: 回傳 null（可能超出免費配額）")
        return None
    if res.status_code != 200:
        print(f"⚠️  {source}: HTTP {res.status_code}")
        return None
    try:
        return res.json()
    except Exception as e:
        print(f"⚠️  {source}: JSON 解析失敗（{e}）")
        return None


def fetch_gdelt() -> list[dict]:
    try:
        res  = requests.get(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            params={"query": "finance OR stock OR semiconductor OR oil OR Fed OR AI",
                    "mode": "ArtList", "maxrecords": 30, "format": "JSON",
                    "timespan": "24h", "sort": "DateDesc"},
            timeout=15,
        )
        data = _safe_json(res, "GDELT")
        if not data:
            return []
        items = [{"source": f"GDELT·{a.get('domain','')}", "title": a.get("title","").strip(),
                  "link": a.get("url","").strip(), "date": _fmt(ts_str=a.get("seendate",""))}
                 for a in (data.get("articles") or [])
                 if a.get("title","").strip() and a.get("url","").strip()]
        print(f"✅ GDELT: {len(items)} 則")
        return items
    except Exception as e:
        print(f"❌ GDELT: {e}")
        return []


def fetch_fred(key: str) -> list[dict]:
    try:
        today    = date.today().isoformat()
        week_ago = (date.today() - timedelta(days=7)).isoformat()
        res  = requests.get(
            "https://api.stlouisfed.org/fred/releases/news",
            params={"api_key": key, "file_type": "json",
                    "realtime_start": week_ago, "realtime_end": today,
                    "limit": 20, "order_by": "update_date", "sort_order": "desc"},
            timeout=15,
        )
        data = _safe_json(res, "FRED")
        if not data:
            return []
        items = []
        for a in (data.get("news") or []):
            t   = (a.get("name") or a.get("title") or "").strip()
            rid = a.get("release_id", "")
            l   = f"https://fred.stlouisfed.org/release?release_id={rid}" if rid else ""
            if t and l:
                items.append({"source": "FRED", "title": f"[經濟數據] {t}", "link": l,
                               "date": _fmt(ts_str=a.get("update_date", a.get("date", "")))})
        print(f"✅ FRED: {len(items)} 則")
        return items
    except Exception as e:
        print(f"❌ FRED: {e}")
        return []


def fetch_finnhub(key: str) -> list[dict]:
    items = []
    for cat in ("general", "technology"):
        try:
            res  = requests.get("https://finnhub.io/api/v1/news",
                                params={"category": cat, "token": key}, timeout=10)
            data = _safe_json(res, f"Finnhub({cat})")
            if not data:
                continue
            for a in data[:20]:
                t = (a.get("headline") or "").strip()
                l = (a.get("url") or "").strip()
                if t and l:
                    items.append({"source": f"Finnhub·{cat}", "title": t, "link": l,
                                  "date": _fmt(ts_unix=a.get("datetime"))})
        except Exception as e:
            print(f"❌ Finnhub({cat}): {e}")
    print(f"✅ Finnhub: {len(items)} 則")
    return items


def fetch_alphavantage(key: str) -> list[dict]:
    try:
        res  = requests.get(
            "https://www.alphavantage.co/query",
            params={"function": "NEWS_SENTIMENT", "topics": "financial_markets,technology,earnings",
                    "sort": "LATEST", "limit": 30, "apikey": key},
            timeout=15,
        )
        data = _safe_json(res, "Alpha Vantage")
        if not data:
            return []
        if "Information" in data:
            print(f"⚠️  Alpha Vantage: {str(data['Information'])[:80]}")
            return []
        items = [{"source": f"AlphaVantage·{a.get('source','')}", "title": a.get("title","").strip(),
                  "link": a.get("url","").strip(), "date": _fmt(ts_str=a.get("time_published",""))}
                 for a in (data.get("feed") or [])
                 if a.get("title","").strip() and a.get("url","").strip()]
        print(f"✅ Alpha Vantage: {len(items)} 則")
        return items
    except Exception as e:
        print(f"❌ Alpha Vantage: {e}")
        return []


def fetch_marketaux(key: str) -> list[dict]:
    try:
        res  = requests.get(
            "https://api.marketaux.com/v1/news/all",
            params={"api_token": key, "language": "en", "limit": 30, "filter_entities": "true"},
            timeout=15,
        )
        data = _safe_json(res, "Marketaux")
        if not data:
            return []
        if data.get("error"):
            print(f"⚠️  Marketaux: {data['error'].get('message','')}")
            return []
        items = [{"source": f"Marketaux·{a.get('source','')}", "title": a.get("title","").strip(),
                  "link": a.get("url","").strip(), "date": _fmt(ts_str=a.get("published_at",""))}
                 for a in (data.get("data") or [])
                 if a.get("title","").strip() and a.get("url","").strip()]
        print(f"✅ Marketaux: {len(items)} 則")
        return items
    except Exception as e:
        print(f"❌ Marketaux: {e}")
        return []


def fetch_currents(key: str) -> list[dict]:
    try:
        res  = requests.get(
            "https://api.currentsapi.services/v1/latest-news",
            params={"apiKey": key, "language": "en", "category": "business,technology,finance"},
            timeout=15,
        )
        data = _safe_json(res, "Currents")
        if not data:
            return []
        items = [{"source": "Currents", "title": a.get("title","").strip(),
                  "link": a.get("url","").strip(), "date": _fmt(ts_str=a.get("published",""))}
                 for a in (data.get("news") or [])[:30]
                 if a.get("title","").strip() and a.get("url","").strip()]
        print(f"✅ Currents: {len(items)} 則")
        return items
    except Exception as e:
        print(f"❌ Currents: {e}")
        return []


def fetch_all() -> list[dict]:
    items = fetch_gdelt()
    if k := os.environ.get("FRED_KEY"):         items += fetch_fred(k)
    if k := os.environ.get("FINNHUB_KEY"):      items += fetch_finnhub(k)
    if k := os.environ.get("ALPHAVANTAGE_KEY"): items += fetch_alphavantage(k)
    if k := os.environ.get("MARKETAUX_KEY"):    items += fetch_marketaux(k)
    if k := os.environ.get("CURRENTS_KEY"):     items += fetch_currents(k)
    return items
