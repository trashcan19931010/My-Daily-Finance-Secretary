import re, time, requests

BATCH = 25

def _eng(t):
    return bool(t) and sum(1 for c in t if ord(c) < 128) / len(t) > 0.6

def _prompt(ts):
    return "請將以下英文新聞標題逐一翻譯成繁體中文。只回傳翻譯結果，每行一個，順序與原文完全相同，不加編號：\n\n" + "\n".join(ts)

def _clean(text, n):
    lines = [re.sub(r'^\d+[.、．]\s*','',l).strip() for l in text.strip().splitlines() if l.strip()]
    return (lines + [""]*n)[:n]

def _groq(ts, key):
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":_prompt(ts)}],"max_tokens":2000,"temperature":0.1},
            timeout=30)
        if r.status_code == 200: return _clean(r.json()["choices"][0]["message"]["content"], len(ts))
        if r.status_code == 429:
            m = re.search(r'try again in (\d+\.?\d*)s', r.json().get("error",{}).get("message",""))
            time.sleep(int(float(m.group(1)))+2 if m else 10)
            r2 = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":_prompt(ts)}],"max_tokens":2000,"temperature":0.1},
                timeout=30)
            if r2.status_code == 200: return _clean(r2.json()["choices"][0]["message"]["content"], len(ts))
    except Exception as e: print(f"  Groq: {e}")
    return None

def _openrouter(ts, key):
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json","HTTP-Referer":"https://github.com"},
            json={"model":"meta-llama/llama-3.3-70b-instruct:free","messages":[{"role":"user","content":_prompt(ts)}],"max_tokens":2000},
            timeout=30)
        if r.status_code == 200: return _clean(r.json()["choices"][0]["message"]["content"], len(ts))
    except Exception as e: print(f"  OpenRouter: {e}")
    return None

def _gemini(ts, key):
    try:
        from google import genai
        c = genai.Client(api_key=key)
        for m in ["gemini-2.0-flash-lite","gemini-2.0-flash","gemini-2.5-flash-preview-05-20"]:
            try:
                return _clean(c.models.generate_content(model=m, contents=_prompt(ts)).text, len(ts))
            except Exception as e:
                err = str(e)
                if "API_KEY_INVALID" in err: print("  Gemini: Key 無效"); return None
                if "404" in err or "NOT_FOUND" in err: continue
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    mo = re.search(r'retry in (\d+\.?\d*)s', err)
                    time.sleep(int(float(mo.group(1)))+3 if mo else 35)
                    try: return _clean(c.models.generate_content(model=m, contents=_prompt(ts)).text, len(ts))
                    except: continue
    except Exception as e: print(f"  Gemini: {e}")
    return None

def translate(news, keys):
    todo = [(i, n["title"]) for i, n in enumerate(news) if _eng(n["title"])]
    if not todo: return news
    batches = [todo[i:i+BATCH] for i in range(0, len(todo), BATCH)]
    print(f"🌐 翻譯 {len(todo)} 則，{len(batches)} 批")
    for b, batch in enumerate(batches, 1):
        idxs, ts = [i for i,_ in batch], [t for _,t in batch]
        res = None
        if keys.get("groq"):        res = _groq(ts, keys["groq"])
        if not res and keys.get("openrouter"): res = _openrouter(ts, keys["openrouter"])
        if not res and keys.get("gemini"):     res = _gemini(ts, keys["gemini"])
        if res:
            for idx, zh in zip(idxs, res):
                if zh: news[idx]["title_zh"] = zh
            print(f"  批次 {b} ✅")
        else:
            print(f"  批次 {b} ⚠️  失敗")
        if b < len(batches): time.sleep(1)
    return news
