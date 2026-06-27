import os, sys
from datetime import datetime, timezone, timedelta
from src import dedup, rss, apis, translator
from src.notifier import Notifier

TZ = timezone(timedelta(hours=8))

def main():
    tok  = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        sys.exit("❌ 未設定 Telegram 環境變數")

    keys = {k: os.environ.get(v) for k, v in {
        "groq": "GROQ_KEY", "openrouter": "OPENROUTER_KEY", "gemini": "GEMINI_API_KEY"
    }.items()}

    sent      = dedup.load()
    all_items = rss.fetch() + apis.fetch_all()
    new_items, new_sent = dedup.filter_new(all_items, sent)
    print(f"\n📰 去重後 {len(new_items)} 則")

    if any(keys.values()) and new_items:
        new_items = translator.translate(new_items, keys)
    else:
        for n in new_items:
            n.setdefault("title_zh", "")

    n = Notifier(tok, chat)
    n.send_all(n.build_messages(new_items))

    sent.update(new_sent)
    dedup.save(sent)
    print("✅ 完成")

if __name__ == "__main__":
    main()
