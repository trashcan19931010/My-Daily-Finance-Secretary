# 📊 台股財經速報

點擊 Telegram 按鈕 → 自動觸發 GitHub Actions → 近 24 小時新聞推播至 Telegram。
無持續運行的程式，完全免費。

---

## 運作原理

```
Telegram 按鈕（永久存在）
        ↓ 點擊
GitHub Pages（靜態網頁）
        ↓ JavaScript 呼叫 GitHub API
GitHub Actions 啟動（約 2–5 分鐘）
        ↓
新聞推播到 Telegram
```

---

## 專案結構

```
finance-secretary/
├── index.html                        # GitHub Pages 觸發頁面
├── setup.py                          # 一次性設定腳本
├── main.py                           # 新聞收集主程式
├── requirements.txt
├── sent_links.json                   # 已發送紀錄（自動產生）
├── .github/workflows/
│   ├── news_direct.yml               # 新聞收集 Workflow（被 Telegram 按鈕觸發）
│   └── setup_button.yml             # 一次性設定 Workflow
└── src/
    ├── rss.py / apis.py              # 新聞收集
    ├── translator.py                 # 英文標題翻譯
    ├── notifier.py                   # Telegram 發送
    └── dedup.py                      # 防重複
```

---

## 新聞來源

### RSS（無需 Key）
| 來源 | 狀態 |
|------|------|
| Yahoo股市 / Yahoo財經 / 科技新報 | ✅ 穩定 |
| Seeking Alpha / MarketWatch | ✅ 穩定 |
| CNBC Finance / CNBC Tech / BBC Business | ✅ 穩定 |
| OilPrice.com | ✅ 穩定 |
| 經濟日報 / ETtoday財經 / 財訊 / 中央社財經 | ⚠️ 測試中 |

### API（需免費申請 Key）
| 服務 | Secret | 免費額度 |
|------|--------|---------|
| GDELT | 不需要 | 完全免費 |
| Finnhub | `FINNHUB_KEY` | 60次/分鐘 |
| Alpha Vantage | `ALPHAVANTAGE_KEY` | 25次/天 |
| Currents API | `CURRENTS_KEY` | 600次/天 |
| FRED | `FRED_KEY` | 無嚴格限制 |
| Marketaux | `MARKETAUX_KEY` | 100次/天 |

### 翻譯（英文標題自動翻譯）
| 服務 | Secret | 免費額度 | 優先順序 |
|------|--------|---------|:-------:|
| Groq | `GROQ_KEY` | 14,400次/天 | ⭐ 第一 |
| OpenRouter | `OPENROUTER_KEY` | 200次/天 | 第二 |
| Gemini | `GEMINI_API_KEY` | 1,500次/天 | 第三 |

---

## 設定步驟（一次性）

### Step 1：Fork / Clone 此 Repo 並設為 Public

> ⚠️ 必須是 Public Repo，才能使用免費的 GitHub Pages 與無限 Actions 分鐘。

### Step 2：修改 index.html

開啟 `index.html`，找到第 47 行，將 `YOUR_USERNAME` 改為你的 GitHub 帳號名稱：

```javascript
const REPO = "YOUR_USERNAME/finance-secretary";
```

Commit 並 Push。

### Step 3：開啟 GitHub Pages

Repository → **Settings → Pages**
- Source：`Deploy from a branch`
- Branch：`main`，Folder：`/ (root)`
- Save

等待約 1 分鐘，取得網址（格式：`https://YOUR_USERNAME.github.io/finance-secretary`）。

### Step 4：建立 GitHub PAT（Trigger Token）

1. GitHub 右上角頭像 → **Settings → Developer settings**
2. **Personal access tokens → Tokens (classic) → Generate new token**
3. 勾選 **`workflow`** 權限（僅需此一項）
4. 複製 Token（`ghp_xxxxxx`）

### Step 5：設定 GitHub Secrets

Repository → **Settings → Secrets → Actions → New repository secret**

| Secret 名稱 | 內容 | 必填 |
|------------|------|:----:|
| `TELEGRAM_BOT_TOKEN` | @BotFather 取得 | ✅ |
| `TELEGRAM_CHAT_ID` | 見下方說明 | ✅ |
| `TRIGGER_PAT` | Step 4 取得的 PAT | ✅ |
| `GROQ_KEY` | console.groq.com | 建議 |
| `FINNHUB_KEY` | finnhub.io | 建議 |
| `ALPHAVANTAGE_KEY` | alphavantage.co | 建議 |
| `CURRENTS_KEY` | currentsapi.services | 建議 |
| `GEMINI_API_KEY` | aistudio.google.com | 可選 |
| `FRED_KEY` | fred.stlouisfed.org/docs/api | 可選 |
| `MARKETAUX_KEY` | marketaux.com | 可選 |
| `OPENROUTER_KEY` | openrouter.ai | 可選 |

### Step 6：取得 Telegram Chat ID

1. Telegram 搜尋 **@BotFather** → `/newbot` → 取得 Bot Token
2. 對 Bot 傳送任意訊息
3. 開啟：`https://api.telegram.org/bot{TOKEN}/getUpdates`
4. 找到 `"chat":{"id":` 後的數字即為 Chat ID

### Step 7：設定 Actions 寫入權限

Repository → **Settings → Actions → General → Workflow permissions**
→ **Read and write permissions** → Save

### Step 8：發送 Telegram 永久按鈕（僅需一次）

1. Actions → 左側選 **「設定 Telegram 按鈕（僅需執行一次）」**
2. **Run workflow**
3. 在 `pages_url` 欄位填入 Step 3 取得的 GitHub Pages 網址
4. **Run workflow**

Telegram 收到訊息後，長按訊息 → **置頂**。

---

## 日常使用

1. 在 Telegram 找到置頂訊息（或捲到上方找到帶按鈕的訊息）
2. 點擊 **📰 獲取最新財經新聞**
3. 瀏覽器短暫開啟顯示「✅ 已觸發！」
4. 約 2–5 分鐘後 Telegram 收到新聞
5. 關閉瀏覽器

---

## 訊息格式

```
📊 財經速報 2026/06/07 14:23
📰 本批次 31 則新消息

新聞時間⏰ 2026/06/07 13:58  |  Reuters
──────────
英文標題📌 Alphabet asks shareholders to foot an $80 billion bill for AI expansion
中文標題📌 Alphabet 要求股東為 AI 擴張買單 800 億美元
──────────
新聞網址🔗 https://reuters.com/...

新聞時間⏰ 2026/06/07 13:44  |  Yahoo股市
──────────
標題📌 台積電 CoWoS 先進封裝下半年供給仍吃緊
──────────
新聞網址🔗 https://tw.stock.yahoo.com/...
```

---

## 安全說明

`TRIGGER_PAT` 儲存在 GitHub Secrets，只在 `setup.py` 執行時使用一次（產生 Telegram 按鈕 URL）。此 Token 只有 `workflow` 權限，僅能觸發 Workflow，無法存取程式碼、Secrets 或其他資料。

---

## 費用

**每月總費用：$0（完全免費）**

---

## 免責聲明

本專案推送之新聞僅供資訊參考，不構成投資建議。投資有風險，請審慎評估。
