"""
一次性設定腳本：發送含永久按鈕的 Telegram 訊息
執行後建議在 Telegram 中「置頂」此訊息
"""
import os
import sys
import requests

BOT_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID     = os.environ.get("TELEGRAM_CHAT_ID")
TRIGGER_PAT = os.environ.get("TRIGGER_PAT")
PAGES_URL   = os.environ.get("PAGES_URL", "").rstrip("/")

if not all([BOT_TOKEN, CHAT_ID, TRIGGER_PAT, PAGES_URL]):
    print("❌ 缺少必要環境變數：TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID / TRIGGER_PAT / PAGES_URL")
    sys.exit(1)

button_url = f"{PAGES_URL}/#{TRIGGER_PAT}"

res = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    json={
        "chat_id":    CHAT_ID,
        "text": (
            "📊 *財經速報*\n\n"
            "點擊下方按鈕，即可觸發近 24 小時最新財經新聞收集。\n"
            "約 2–5 分鐘後新聞將推播至此對話。\n\n"
            "💡 建議將此訊息*置頂*，方便隨時使用。"
        ),
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "📰 獲取最新財經新聞", "url": button_url}
            ]]
        }
    },
    timeout=10,
)

if res.status_code == 200:
    print("✅ Telegram 按鈕訊息已發送！")
    print("👉 請在 Telegram 中找到這則訊息並「置頂」")
else:
    print(f"❌ 發送失敗：{res.status_code} {res.text}")
    sys.exit(1)
