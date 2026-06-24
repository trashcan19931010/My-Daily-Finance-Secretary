import os
import sys
from datetime import datetime, timezone, timedelta
from src import dedup, rss, apis, translator
from src.notifier import Notifier

TZ_TAIPEI = timezone(timedelta(hours=8))


def main():
    print(f"🚀 [{datetime.now(TZ_TAIPEI).strftime('%Y-%m-%d %H:%M')} 台北時間]")

    TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TG_CHAT  = os.environ.get("TELEGRAM_CHAT_ID")
    if not TG_TOKEN or not TG_CHAT:
        print("❌ 未設定 Telegram 環境變數")
        sys.exit(1)

    keys = {
        "groq":       os.environ.get("GROQ_KEY"),
        "openrouter": os.environ.get("OPENROUTER_KEY"),
        "gemini":     os.environ.get("GEMINI_API_KEY"),
    }

    sent      = dedup.load()

    print("\n── RSS ──────────────────────────")
    all_items = rss.fetch()
    print("\n── API ──────────────────────────")
    all_items += apis.fetch_all()

    new_items, new_sent = dedup.filter_new(all_items, sent)
    print(f"\n📰 去重後 {len(new_items)} 則新消息")

    if any(keys.values()) and new_items:
        new_items = translator.translate(new_items, keys)
    else:
        for n in new_items:
            n.setdefault("title_zh", "")

    notifier = Notifier(TG_TOKEN, TG_CHAT)
    messages = notifier.build_messages(new_items)
    print(f"📤 發送 {len(messages)} 則訊息...")
    notifier.send_all(messages)

    sent.update(new_sent)
    dedup.save(sent)
    print("✅ 完成！")


if __name__ == "__main__":
    main()
