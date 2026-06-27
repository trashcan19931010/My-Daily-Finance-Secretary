import feedparser
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
UA = {"User-Agent": "Mozilla/5.0 (compatible; FinanceBot/2.0)"}

SOURCES = [
    ("Yahoo股市",     "https://tw.stock.yahoo.com/rss"),
    ("Yahoo財經",     "https://tw.news.yahoo.com/rss/finance"),
    ("科技新報",      "https://technews.tw/feed/"),
    ("經濟日報",      "https://money.udn.com/rssfeed/news/2/6638"),
    ("ETtoday財經",   "https://finance.ettoday.net/rss.xml"),
    ("財訊",          "https://www.wealth.com.tw/feed"),
    ("中央社財經",    "https://www.cna.com.tw/rss/aall.aspx"),
    ("Seeking Alpha", "https://seekingalpha.com/feed.xml"),
    ("MarketWatch",   "https://feeds.marketwatch.com/marketwatch/topstories/"),
    ("CNBC Finance",  "https://www.cnbc.com/id/10001147/device/rss/rss.html"),
    ("CNBC Tech",     "https://www.cnbc.com/id/19854910/device/rss/rss.html"),
    ("BBC Business",  "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("OilPrice.com",  "https://oilprice.com/rss/main"),
]

def _dt(e):
    t = e.get("published_parsed") or e.get("updated_parsed")
    return datetime(*t[:6], tzinfo=timezone.utc) if t else None

def _fmt(dt):
    return dt.astimezone(TZ).strftime("%Y/%m/%d %H:%M") if dt else ""

def fetch():
    cutoff, items = datetime.now(TZ) - timedelta(hours=24), []
    for name, url in SOURCES:
        try:
            feed = feedparser.parse(url, request_headers=UA)
            if not feed.entries:
                print(f"⚠️  {name}: 無文章")
                continue
            new = old = 0
            for e in feed.entries[:30]:
                lnk, ttl = (e.get("link") or "").strip(), (e.get("title") or "").strip()
                if not lnk or not ttl:
                    continue
                dt = _dt(e)
                if dt and dt.astimezone(TZ) < cutoff:
                    old += 1; continue
                items.append({"source": name, "title": ttl, "link": lnk, "date": _fmt(dt)})
                new += 1
            if new:   print(f"✅ {name}: {new} 則")
            elif old: print(f"⏳ {name}: 0 則（{old} 則超過24h）")
            else:     print(f"⚠️  {name}: 無有效文章")
        except Exception as e:
            print(f"❌ {name}: {e}")
    return items
