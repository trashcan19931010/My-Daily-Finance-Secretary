import re
import time
import requests

BATCH_SIZE = 25


def _is_english(text: str) -> bool:
    if not text:
        return False
    return sum(1 for c in text if ord(c) < 128) / len(text) > 0.6


def _prompt(titles: list[str]) -> str:
    return (
        "請將以下英文新聞標題逐一翻譯成繁體中文。\n"
        "只回傳翻譯結果，每行一個，順序與原文完全相同，不加編號或任何說明：\n\n"
        + "\n".join(titles)
    )


def _clean(text: str, count: int) -> list[str]:
    lines = [re.sub(r'^\d+[.、．]\s*', '', l).strip()
             for l in text.strip().splitlines() if l.strip()]
    while len(lines) < count:
        lines.append("")
    return lines[:count]


def _groq(titles: list[str], key: str) -> list[str] | None:
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": _prompt(titles)}],
                  "max_tokens": 2000, "temperature": 0.1},
            timeout=30,
        )
        if res.status_code == 200:
            return _clean(res.json()["choices"][0]["message"]["content"], len(titles))
        if res.status_code == 429:
            m = re.search(r'try again in (\d+\.?\d*)s',
                          res.json().get("error", {}).get("message", ""))
            time.sleep(int(float(m.group(1))) + 2 if m else 10)
            res2 = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile",
                      "messages": [{"role": "user", "content": _prompt(titles)}],
                      "max_tokens": 2000, "temperature": 0.1},
                timeout=30,
            )
            if res2.status_code == 200:
                return _clean(res2.json()["choices"][0]["message"]["content"], len(titles))
        print(f"  ⚠️  Groq HTTP {res.status_code}")
        return None
    except Exception as e:
        print(f"  ⚠️  Groq: {e}")
        return None


def _openrouter(titles: list[str], key: str) -> list[str] | None:
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                     "HTTP-Referer": "https://github.com"},
            json={"model": "meta-llama/llama-3.3-70b-instruct:free",
                  "messages": [{"role": "user", "content": _prompt(titles)}],
                  "max_tokens": 2000},
            timeout=30,
        )
        if res.status_code == 200:
            return _clean(res.json()["choices"][0]["message"]["content"], len(titles))
        print(f"  ⚠️  OpenRouter HTTP {res.status_code}")
        return None
    except Exception as e:
        print(f"  ⚠️  OpenRouter: {e}")
        return None


def _gemini(titles: list[str], key: str) -> list[str] | None:
    try:
        from google import genai
        client = genai.Client(api_key=key)
        for model in ["gemini-2.0-flash-lite", "gemini-2.0-flash",
                      "gemini-2.5-flash-preview-05-20"]:
            try:
                resp = client.models.generate_content(model=model, contents=_prompt(titles))
                return _clean(resp.text, len(titles))
            except Exception as e:
                err = str(e)
                if "API_KEY_INVALID" in err:
                    print("  ❌ GEMINI_API_KEY 無效")
                    return None
                if "404" in err or "NOT_FOUND" in err:
                    continue
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    m = re.search(r'retry in (\d+\.?\d*)s', err)
                    time.sleep(int(float(m.group(1))) + 3 if m else 35)
                    try:
                        resp2 = client.models.generate_content(model=model, contents=_prompt(titles))
                        return _clean(resp2.text, len(titles))
                    except Exception:
                        continue
                print(f"  ⚠️  Gemini {model}: {e}")
        return None
    except Exception as e:
        print(f"  ⚠️  Gemini: {e}")
        return None


def translate(news_list: list[dict], keys: dict) -> list[dict]:
    to_tr = [(i, n["title"]) for i, n in enumerate(news_list) if _is_english(n["title"])]
    if not to_tr:
        print("ℹ️  無英文標題，跳過翻譯")
        return news_list

    batches = [to_tr[i:i+BATCH_SIZE] for i in range(0, len(to_tr), BATCH_SIZE)]
    print(f"🌐 翻譯 {len(to_tr)} 則，共 {len(batches)} 批")

    for b_num, batch in enumerate(batches, 1):
        indices = [i for i, _ in batch]
        titles  = [t for _, t in batch]
        print(f"  批次 {b_num}/{len(batches)}（{len(titles)} 則）")

        result = None
        if keys.get("groq"):
            print("    → Groq")
            result = _groq(titles, keys["groq"])
        if not result and keys.get("openrouter"):
            print("    → OpenRouter")
            result = _openrouter(titles, keys["openrouter"])
        if not result and keys.get("gemini"):
            print("    → Gemini")
            result = _gemini(titles, keys["gemini"])

        if result:
            for idx, zh in zip(indices, result):
                if zh:
                    news_list[idx]["title_zh"] = zh
            print(f"    ✅ 批次 {b_num} 完成")
        else:
            print(f"    ⚠️  批次 {b_num} 全部失敗，保留英文原文")

        if b_num < len(batches):
            time.sleep(1)

    return news_list
