import time, requests
from datetime import datetime, timezone, timedelta

TZ  = timezone(timedelta(hours=8))
SEP = "─" * 10

class Notifier:
    def __init__(self, token, chat_id):
        self.url  = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat = chat_id

    def _send(self, text):
        for mode in ["Markdown", ""]:
            try:
                r = requests.post(self.url, json={"chat_id":self.chat,"text":text,"parse_mode":mode,"disable_web_page_preview":True}, timeout=10)
                if r.status_code == 200: return True
                if r.status_code == 429: time.sleep(r.json().get("parameters",{}).get("retry_after",5))
            except: pass
        return False

    def send_all(self, msgs):
        for i, m in enumerate(msgs, 1):
            if m.strip():
                print(f"{'✅' if self._send(m) else '❌'} {i}/{len(msgs)}")
            time.sleep(0.5)

    @staticmethod
    def fmt(n):
        d = n.get("date") or datetime.now(TZ).strftime("%Y/%m/%d %H:%M")
        lines = [f"新聞時間⏰ {d}  |  {n.get('source','')}", SEP]
        if n.get("title_zh"):
            lines += [f"英文標題📌 {n['title']}", f"中文標題📌 {n['title_zh']}"]
        else:
            lines.append(f"標題📌 {n['title']}")
        lines += [SEP, f"新聞網址🔗 {n['link']}"]
        return "\n".join(lines)

    def build_messages(self, news):
        now = datetime.now(TZ).strftime("%Y/%m/%d %H:%M")
        if not news:
            return [f"📭 {now}\n近 24 小時內無新消息。"]
        return [f"📊 財經速報 {now}\n📰 本批次 {len(news)} 則新消息"] + [self.fmt(n) for n in news]
