import os, sys, requests

TOKEN   = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT    = os.environ["TELEGRAM_CHAT_ID"]
PAT     = os.environ["TRIGGER_PAT"]
URL     = os.environ["PAGES_URL"].rstrip("/")

res = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
    "chat_id": CHAT,
    "text": "📊 *財經速報*\n\n點擊按鈕獲取近 24 小時最新財經新聞（約 2–5 分鐘後推播）\n\n💡 建議將此訊息*置頂*",
    "parse_mode": "Markdown",
    "reply_markup": {"inline_keyboard": [[{"text": "📰 獲取最新財經新聞", "url": f"{URL}/#{PAT}"}]]}
}, timeout=10)

print("✅ 已發送" if res.status_code == 200 else f"❌ 失敗：{res.text}")
