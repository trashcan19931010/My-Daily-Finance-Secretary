import feedparser
import requests
from datetime import datetime, timezone, timedelta

TZ_TAIPEI = timezone(timedelta(hours=8))
UA        = {"User-Agent": "Mozilla/5.0 (compatible; FinanceBot/2.0; +https://github.com)"}

RSS_SOURCES = [
    # 台灣（穩定）
    {"name": "Yahoo股市",     "url": "https://tw.stock.yahoo.com/rss"},
    {"name": "Yahoo財經",     "url": "https://tw.news.yahoo.com/rss/finance"},
    {"name": "科技新報",      "url": "https://technews.tw/feed/"},
    # 台灣（測試中）
    {"name": "經濟日報",      "url": "https://money.udn.com/rssfeed/news/2/6638"},
    {"name": "ETtoday財經",   "url": "https://finance.ettoday.net/rss.xml"},
    {"name": "財訊",          "url": "https://www.wealth.com.tw/feed"},
    {"name": "中央社財經",    "url": "https://www.cna.com.tw/rss/aall.aspx"},
    # 國際（穩定）
    {"name": "Seeking Alpha", "url": "https://seekingalpha.com/feed.xml"},
    {"name": "MarketWatch",   "url": "https://feeds.marketwatch.com/marketwatch/topstories/"},
    {"name": "CNBC Finance",  "url": "https://www.cnbc.com/id/10001147/device/rss/rss.html"},
    {"name": "CNBC Tech",     "url": "https://www.cnbc.com/id/19854910/device/rss/rss.html"},
    {"name": "BBC Business",  "url": "https://feeds.bbci.co.uk/news/business/rss.xml"},
    {"name": "OilPrice.com",  "url": "https://oilprice.com/rss/main"},
]


def _pub_dt(entry) -> datetime | None:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if t:
        try:
            return datetime(*t[:6], tzinfo=timezone.utc)
        except Exception:
            pass
    return None


def _fmt(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.astimezone(TZ_TAIPEI).strftime("%Y/%m/%d %H:%M")


def fetch() -> list[dict]:
    cutoff = datetime.now(TZ_TAIPEI) - timedelta(hours=24)
    items  = []

    for src in RSS_SOURCES:
        try:
            feed    = feedparser.parse(src["url"], request_headers=UA)
            entries = feed.entries
            status  = getattr(feed, "status", None)

            if not entries:
                print(f"⚠️  RSS {src['name']}: 無文章（HTTP {status}）")
                continue

            new_count = old_count = 0
            for e in entries[:30]:
                link  = (e.get("link") or "").strip()
                title = (e.get("title") or "").strip()
                if not link or not title:
                    continue
                pub = _pub_dt(e)
                if pub and pub.astimezone(TZ_TAIPEI) < cutoff:
                    old_count += 1
                    continue
                items.append({"source": src["name"], "title": title,
                               "link": link, "date": _fmt(pub)})
                new_count += 1

            if new_count > 0:
                print(f"✅ RSS {src['name']}: {new_count} 則新")
            elif old_count > 0:
                print(f"⏳ RSS {src['name']}: 0 則新（{old_count} 則超過24小時）")
            else:
                print(f"⚠️  RSS {src['name']}: 無有效文章")
        except Exception as e:
            print(f"❌ RSS {src['name']}: {e}")

    return items
