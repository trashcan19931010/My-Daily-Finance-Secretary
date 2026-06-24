import time
import requests
from datetime import datetime, timezone, timedelta

TZ_TAIPEI = timezone(timedelta(hours=8))
SEP       = "─" * 10


class Notifier:

    def __init__(self, token: str, chat_id: str):
        self.url     = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    def _send(self, text: str) -> bool:
        for parse_mode in ["Markdown", ""]:
            try:
                res = requests.post(self.url, json={
                    "chat_id": self.chat_id, "text": text,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": True,
                }, timeout=10)
                if res.status_code == 200:
                    return True
                if res.status_code == 429:
                    time.sleep(res.json().get("parameters", {}).get("retry_after", 5))
            except Exception:
                pass
        return False

    def send_all(self, messages: list[str]):
        total = len(messages)
        for i, msg in enumerate(messages, 1):
            if msg.strip():
                ok = self._send(msg)
                print(f"{'✅' if ok else '❌'} {i}/{total}")
            time.sleep(0.5)

    @staticmethod
    def fmt(n: dict) -> str:
        date_str = n.get("date") or datetime.now(TZ_TAIPEI).strftime("%Y/%m/%d %H:%M")
        lines    = [f"新聞時間⏰ {date_str}  |  {n.get('source', '')}", SEP]
        if n.get("title_zh"):
            lines.append(f"英文標題📌 {n['title']}")
            lines.append(f"中文標題📌 {n['title_zh']}")
        else:
            lines.append(f"標題📌 {n['title']}")
        lines += [SEP, f"新聞網址🔗 {n['link']}"]
        return "\n".join(lines)

    def build_messages(self, news_list: list[dict]) -> list[str]:
        now = datetime.now(TZ_TAIPEI).strftime("%Y/%m/%d %H:%M")
        if not news_list:
            return [f"📭 {now}\n近 24 小時內無新消息。"]
        return [f"📊 財經速報 {now}\n📰 本批次 {len(news_list)} 則新消息"] + \
               [self.fmt(n) for n in news_list]
