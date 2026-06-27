# 📊 台股財經速報

Telegram 按鈕 → GitHub Pages → GitHub Actions → 近 24 小時新聞推播至 Telegram。
無需持續運行任何程式，完全免費。

---

## 運作流程

```
Telegram 置頂訊息（永久存在）
        ↓ 點擊「📰 獲取最新財經新聞」
GitHub Pages（靜態網頁，永久存在）
        ↓ JavaScript 呼叫 GitHub API
GitHub Actions 啟動（跑完自動結束）
        ↓ 約 2–5 分鐘
新聞推播到 Telegram
```

也可直接從 GitHub Actions → **「財經新聞推播」** → Run workflow 手動觸發。

---

## 觸發方式

| 方式 | 步驟 |
|------|------|
| Telegram 按鈕 | 點置頂訊息按鈕 → 瀏覽器開啟 → 自動觸發 |
| GitHub 手動 | Actions → 財經新聞推播 → Run workflow |

---

## 專案結構

```
finance-secretary/
├── index.html                   # GitHub Pages 觸發頁面
├── setup.py                     # 發送 Telegram 按鈕訊息（一次性）
├── main.py                      # 新聞收集與推播
├── requirements.txt
├── sent_links.json              # 已發送紀錄（自動產生）
├── .github/workflows/
│   ├── news_direct.yml          # 新聞推播 Workflow
│   └── setup_button.yml        # 一次性設定 Workflow
└── src/
    ├── rss.py / apis.py         # 新聞收集
    ├── translator.py            # 英文翻譯
    ├── notifier.py              # Telegram 發送
    └── dedup.py                 # 防重複
```

---

## 新聞來源

### RSS（無需 Key）
| 來源 | 狀態 |
|------|------|
| Yahoo股市 / Yahoo財經 / 科技新報 | ✅ 穩定 |
| Seeking Alpha / MarketWatch / CNBC / BBC / OilPrice | ✅ 穩定 |
| 經濟日報 / ETtoday財經 / 財訊 / 中央社財經 | ⚠️ 測試中 |

### API（需申請免費 Key）
| 服務 | Secret | 免費額度 |
|------|--------|---------|
| GDELT | 不需要 | 完全免費 |
| Finnhub | `FINNHUB_KEY` | 60次/分鐘 |
| Alpha Vantage | `ALPHAVANTAGE_KEY` | 25次/天 |
| Currents API | `CURRENTS_KEY` | 600次/天 |
| FRED | `FRED_KEY` | 無嚴格限制 |
| Marketaux | `MARKETAUX_KEY` | 100次/天 |

### 翻譯
| 服務 | Secret | 免費額度 | 優先 |
|------|--------|---------|:----:|
| Groq | `GROQ_KEY` | 14,400次/天 | 1 |
| OpenRouter | `OPENROUTER_KEY` | 200次/天 | 2 |
| Gemini | `GEMINI_API_KEY` | 1,500次/天 | 3 |

---

## 一次性設定步驟

### 1. Repo 設為 Public
Settings → General → Danger Zone → Change repository visibility → **Public**

### 2. 修改 index.html
開啟 `index.html`，將第 23 行的 `YOUR_USERNAME` 改為你的 GitHub 帳號：
```js
const REPO = "YOUR_USERNAME/finance-secretary";
```

### 3. 開啟 GitHub Pages
Settings → Pages → Source: **Deploy from a branch** → Branch: `main` / `/ (root)` → Save

取得網址格式：`https://YOUR_USERNAME.github.io/finance-secretary`

### 4. 建立 TRIGGER_PAT
GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
→ Generate new token → 勾選 **`workflow`** → 複製 Token

### 5. 設定 GitHub Secrets
Settings → Secrets → Actions → New repository secret

| Secret | 說明 | 必填 |
|--------|------|:----:|
| `TELEGRAM_BOT_TOKEN` | @BotFather 取得 | ✅ |
| `TELEGRAM_CHAT_ID` | 見下方 | ✅ |
| `TRIGGER_PAT` | 步驟 4 的 Token | ✅ |
| `GROQ_KEY` | console.groq.com | 建議 |
| `FINNHUB_KEY` | finnhub.io | 建議 |
| `ALPHAVANTAGE_KEY` | alphavantage.co | 建議 |
| `CURRENTS_KEY` | currentsapi.services | 建議 |

**取得 Chat ID：**
1. 對 Bot 傳任意訊息
2. 開啟 `https://api.telegram.org/bot{TOKEN}/getUpdates`
3. 找到 `"chat":{"id":` 後的數字

### 6. 開啟 Actions 寫入權限
Settings → Actions → General → Workflow permissions → **Read and write permissions** → Save

### 7. 發送 Telegram 永久按鈕（只做一次）
Actions → **「設定 Telegram 按鈕（僅需一次）」** → Run workflow
→ 填入步驟 3 的 GitHub Pages 網址 → Run workflow

Telegram 收到訊息後長按 → **置頂**。

---

## 訊息格式

```
📊 財經速報 2026/06/07 14:23
📰 本批次 28 則新消息

新聞時間⏰ 2026/06/07 13:58  |  Reuters
──────────
英文標題📌 Alphabet asks shareholders to foot an $80 billion bill for AI
中文標題📌 Alphabet 要求股東為 AI 擴張買單 800 億美元
──────────
新聞網址🔗 https://reuters.com/...
```

---

## 費用：$0（完全免費）

---

## 免責聲明

本專案推送之新聞僅供資訊參考，不構成投資建議。
