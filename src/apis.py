import os, requests
from datetime import datetime, date, timezone, timedelta

TZ = timezone(timedelta(hours=8))

def _fmt(ts_unix=None, ts_str=None):
    try:
        if ts_unix:
            dt = datetime.fromtimestamp(int(ts_unix), tz=timezone.utc)
        else:
            s = str(ts_str or "").strip().replace("Z", "+00:00")
            for f in ("%Y%m%dT%H%M%SZ","%Y%m%d%H%M%S","%Y-%m-%dT%H:%M:%S%z",
                      "%Y-%m-%dT%H:%M:%S","%Y-%m-%d %H:%M:%S","%Y-%m-%d %H:%M","%Y%m%d"):
                try:
                    dt = datetime.strptime(s, f)
                    if not dt.tzinfo: dt = dt.replace(tzinfo=timezone.utc)
                    break
                except: continue
            else: return ""
        return dt.astimezone(TZ).strftime("%Y/%m/%d %H:%M")
    except: return ""

def _j(res, src):
    t = (res.text or "").strip()
    if not t or t.lower() in ("null","none"): print(f"⚠️  {src}: 空回應"); return None
    if res.status_code != 200: print(f"⚠️  {src}: HTTP {res.status_code}"); return None
    try: return res.json()
    except Exception as e: print(f"⚠️  {src}: {e}"); return None

def _items(rows, src_key, title_key, link_key, date_fn):
    return [{"source": src_key, "title": r.get(title_key,"").strip(),
             "link": r.get(link_key,"").strip(), "date": date_fn(r)}
            for r in rows if r.get(title_key,"").strip() and r.get(link_key,"").strip()]

def gdelt():
    try:
        r = requests.get("https://api.gdeltproject.org/api/v2/doc/doc", params={
            "query":"finance OR stock OR semiconductor OR oil OR Fed OR AI",
            "mode":"ArtList","maxrecords":30,"format":"JSON","timespan":"24h","sort":"DateDesc"
        }, timeout=15)
        d = _j(r, "GDELT")
        if not d: return []
        out = [{"source":f"GDELT·{a.get('domain','')}","title":a.get("title","").strip(),
                "link":a.get("url","").strip(),"date":_fmt(ts_str=a.get("seendate",""))}
               for a in (d.get("articles") or []) if a.get("title","").strip() and a.get("url","").strip()]
        print(f"✅ GDELT: {len(out)} 則"); return out
    except Exception as e: print(f"❌ GDELT: {e}"); return []

def finnhub(key):
    out = []
    for cat in ("general","technology"):
        try:
            r = requests.get("https://finnhub.io/api/v1/news", params={"category":cat,"token":key}, timeout=10)
            d = _j(r, f"Finnhub({cat})")
            if d: out += [{"source":f"Finnhub·{cat}","title":a.get("headline","").strip(),
                            "link":a.get("url","").strip(),"date":_fmt(ts_unix=a.get("datetime"))}
                           for a in d[:20] if a.get("headline","").strip() and a.get("url","").strip()]
        except Exception as e: print(f"❌ Finnhub({cat}): {e}")
    print(f"✅ Finnhub: {len(out)} 則"); return out

def alphavantage(key):
    try:
        r = requests.get("https://www.alphavantage.co/query", params={
            "function":"NEWS_SENTIMENT","topics":"financial_markets,technology,earnings",
            "sort":"LATEST","limit":30,"apikey":key}, timeout=15)
        d = _j(r, "AlphaVantage")
        if not d: return []
        if "Information" in d: print(f"⚠️  AlphaVantage: {str(d['Information'])[:60]}"); return []
        out = _items(d.get("feed") or [], "AlphaVantage", "title", "url",
                     lambda a: _fmt(ts_str=a.get("time_published","")))
        print(f"✅ AlphaVantage: {len(out)} 則"); return out
    except Exception as e: print(f"❌ AlphaVantage: {e}"); return []

def marketaux(key):
    try:
        r = requests.get("https://api.marketaux.com/v1/news/all",
                         params={"api_token":key,"language":"en","limit":30,"filter_entities":"true"}, timeout=15)
        d = _j(r, "Marketaux")
        if not d: return []
        if d.get("error"): print(f"⚠️  Marketaux: {d['error'].get('message','')}"); return []
        out = _items(d.get("data") or [], "Marketaux", "title", "url",
                     lambda a: _fmt(ts_str=a.get("published_at","")))
        print(f"✅ Marketaux: {len(out)} 則"); return out
    except Exception as e: print(f"❌ Marketaux: {e}"); return []

def currents(key):
    try:
        r = requests.get("https://api.currentsapi.services/v1/latest-news",
                         params={"apiKey":key,"language":"en","category":"business,technology,finance"}, timeout=15)
        d = _j(r, "Currents")
        if not d: return []
        out = _items((d.get("news") or [])[:30], "Currents", "title", "url",
                     lambda a: _fmt(ts_str=a.get("published","")))
        print(f"✅ Currents: {len(out)} 則"); return out
    except Exception as e: print(f"❌ Currents: {e}"); return []

def fred(key):
    try:
        today = date.today().isoformat()
        week_ago = (date.today() - timedelta(days=7)).isoformat()
        r = requests.get("https://api.stlouisfed.org/fred/releases/news", params={
            "api_key":key,"file_type":"json","realtime_start":week_ago,
            "realtime_end":today,"limit":20,"order_by":"update_date","sort_order":"desc"}, timeout=15)
        d = _j(r, "FRED")
        if not d: return []
        out = [{"source":"FRED","title":f"[經濟數據] {(a.get('name') or a.get('title',''))[:].strip()}",
                "link":f"https://fred.stlouisfed.org/release?release_id={a.get('release_id','')}",
                "date":_fmt(ts_str=a.get("update_date",a.get("date","")))}
               for a in (d.get("news") or []) if a.get("name") or a.get("title")]
        print(f"✅ FRED: {len(out)} 則"); return out
    except Exception as e: print(f"❌ FRED: {e}"); return []

def fetch_all():
    g = os.environ.get
    out = gdelt()
    if k := g("FINNHUB_KEY"):      out += finnhub(k)
    if k := g("ALPHAVANTAGE_KEY"): out += alphavantage(k)
    if k := g("MARKETAUX_KEY"):    out += marketaux(k)
    if k := g("CURRENTS_KEY"):     out += currents(k)
    if k := g("FRED_KEY"):         out += fred(k)
    return out
