# 誠品寵物書籍新書 Email 通知設定指南

## 功能說明
此系統會每天自動檢查誠品寵物書籍分類，當有新書上架時，會發送 Email 通知給所有訂閱者。

支援兩種訂閱方式：
1. **Google Forms + Sheets** - 讓訪客透過表單訂閱（推薦）
2. **環境變數** - 直接設定單一收件人（向下相容）

---

## 設定步驟

### 步驟 1：建立 GitHub Repository

1. 前往 [GitHub](https://github.com) 登入你的帳號
2. 點擊右上角 **+** → **New repository**
3. 輸入 Repository 名稱，例如 `pet-books-notifier`
4. 選擇 **Private**（建議，因為會存放書籍資料）
5. 點擊 **Create repository**

### 步驟 2：上傳檔案到 GitHub

在本地專案資料夾執行以下命令：

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的帳號/pet-books-notifier.git
git push -u origin main
```

### 步驟 3：取得 Gmail 應用程式密碼

Gmail 不允許直接使用帳號密碼登入，需要建立「應用程式密碼」：

1. 前往 [Google 帳戶](https://myaccount.google.com/)
2. 左側選單點擊 **安全性**
3. 確認已開啟 **兩步驟驗證**（如未開啟請先啟用）
4. 在「兩步驟驗證」區塊下方，點擊 **應用程式密碼**
5. 選擇應用程式：**郵件**
6. 選擇裝置：**其他**，輸入名稱如「新書通知」
7. 點擊 **產生**
8. 複製顯示的 16 位密碼（格式如：`abcd efgh ijkl mnop`）

> ⚠️ 這個密碼只會顯示一次，請妥善保存！

### 步驟 4：設定 GitHub Secrets

1. 進入你的 GitHub Repository
2. 點擊 **Settings** → **Secrets and variables** → **Actions**
3. 點擊 **New repository secret**，新增以下三個 Secrets：

| Name | Value |
|------|-------|
| `SENDER_EMAIL` | 你的 Gmail 地址，例如 `yourname@gmail.com` |
| `SENDER_PASSWORD` | 步驟 3 取得的 16 位應用程式密碼 |
| `RECIPIENT_EMAIL` | （選填）單一收件人 Email |
| `GOOGLE_SHEETS_ID` | （選填）Google Sheets 的 ID |
| `GOOGLE_CREDENTIALS_JSON` | （選填）Google Service Account 的 JSON 金鑰 |

### 步驟 5：設定訂閱表單（選填，推薦）

如果想讓訪客自行訂閱，請按照以下步驟設定 Google Forms + Sheets：

#### 5.1 建立 Google Form

1. 前往 [Google Forms](https://forms.google.com)
2. 建立新表單
3. 表單標題：「訂閱寵物書籍新書通知」
4. 新增一個問題：
   - 問題類型：**簡答**
   - 問題內容：「你的 Email」
   - 設為**必填**
5. 點擊右上角 **傳送**，複製表單連結

#### 5.2 設定 Google Sheets

1. 在 Google Form 編輯頁面，點擊上方 **回覆** 分頁
2. 點擊 Google Sheets 圖示，建立試算表
3. 開啟試算表後，從網址列複製 Sheets ID
   - 網址格式：`https://docs.google.com/spreadsheets/d/【這裡就是 SHEETS_ID】/edit`

#### 5.3 建立 Google Cloud Service Account

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 **Google Sheets API**：
   - 前往 APIs & Services → Library
   - 搜尋 "Google Sheets API"
   - 點擊 **啟用**
4. 建立 Service Account：
   - 前往 APIs & Services → Credentials
   - 點擊 **Create Credentials** → **Service Account**
   - 輸入名稱，例如 `pet-books-notifier`
   - 點擊 **Create and Continue**
   - 角色選擇 **Viewer**（檢視者）
   - 點擊 **Done**
5. 下載 JSON 金鑰：
   - 點擊剛建立的 Service Account
   - 切換到 **Keys** 分頁
   - 點擊 **Add Key** → **Create new key**
   - 選擇 **JSON**，下載金鑰檔案

#### 5.4 共用 Google Sheets 給 Service Account

1. 開啟金鑰 JSON 檔案，找到 `client_email` 欄位
2. 開啟你的 Google Sheets
3. 點擊右上角 **共用**
4. 將 `client_email` 的 Email 加入（例如 `pet-books@your-project.iam.gserviceaccount.com`）
5. 權限設為 **檢視者**

#### 5.5 設定 GitHub Secrets

1. 在 GitHub Repository 新增以下 Secrets：

| Name | Value |
|------|-------|
| `GOOGLE_SHEETS_ID` | Google Sheets 的 ID（從網址複製） |
| `GOOGLE_CREDENTIALS_JSON` | Service Account JSON 金鑰的**完整內容**（用文字編輯器打開複製） |

#### 5.6 更新網站表單連結

1. 編輯 `index.html`
2. 找到 `SUBSCRIBE_FORM_URL` 變數
3. 將 `'YOUR_GOOGLE_FORM_URL'` 替換成你的 Google Form 連結

```javascript
const SUBSCRIBE_FORM_URL = 'https://docs.google.com/forms/d/e/xxx/viewform';
```

### 步驟 6：啟用 GitHub Actions

1. 進入 Repository 的 **Actions** 分頁
2. 如果看到提示，點擊 **I understand my workflows, go ahead and enable them**
3. 點擊左側 **Check New Books**
4. 點擊 **Run workflow** → **Run workflow** 手動測試一次

---

## 訂閱者管理

### 查看訂閱者

開啟連結至 Google Form 的 Google Sheets，即可看到所有訂閱者的 Email。

### 新增訂閱者

訂閱者可透過：
1. 網站上的「訂閱通知」按鈕填寫 Google Form
2. 直接在 Google Sheets 中手動新增 Email（第一欄）

### 移除訂閱者

在 Google Sheets 中刪除該訂閱者的整列資料即可。

---

## 執行時間

- 預設每天台灣時間 **早上 9:00** 自動執行
- 如需更改時間，編輯 `.github/workflows/check-new-books.yml` 中的 cron 設定：

```yaml
schedule:
  - cron: '0 1 * * *'  # UTC 時間，台灣 = UTC+8
```

常用 cron 設定：
| 台灣時間 | UTC cron |
|---------|----------|
| 每天 06:00 | `0 22 * * *` |
| 每天 09:00 | `0 1 * * *` |
| 每天 12:00 | `0 4 * * *` |
| 每天 18:00 | `0 10 * * *` |
| 每天 21:00 | `0 13 * * *` |

---

## 手動執行

隨時可以手動觸發檢查：

1. 進入 GitHub Repository 的 **Actions** 分頁
2. 點擊左側 **Check New Books**
3. 點擊 **Run workflow** → **Run workflow**

---

## 檢視執行紀錄

1. 進入 **Actions** 分頁
2. 點擊任一執行紀錄
3. 點擊 **check-books** 查看詳細 log

---

## 本地測試

也可以在本機測試腳本：

```bash
# 安裝依賴
pip install playwright
playwright install chromium

# 設定環境變數（Windows PowerShell）
$env:SENDER_EMAIL = "your@gmail.com"
$env:SENDER_PASSWORD = "your-app-password"
$env:RECIPIENT_EMAIL = "recipient@email.com"

# 執行
python new_books_checker.py
```

---

## Email 通知範例

當有新書上架時，你會收到這樣的 Email：

**主旨：** 📚 誠品寵物書籍新書通知 - 3 本新書上架！

**內容包含：**
- 新書名稱
- 作者
- 售價
- 購買連結

---

## 常見問題

### Q: GitHub Actions 沒有執行？
A: 確認 Repository 的 Actions 功能已啟用。前往 Settings → Actions → General，選擇 "Allow all actions"。

### Q: Email 發送失敗？
A:
1. 確認 Gmail 已開啟兩步驟驗證
2. 確認使用的是應用程式密碼，不是一般密碼
3. 確認 Secrets 名稱正確（區分大小寫）

### Q: 如何停止通知？
A: 進入 Repository Settings → Actions → General，選擇 "Disable actions"。

---

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `new_books_checker.py` | 新書檢查與通知主程式 |
| `index.html` | 網站前端（含訂閱按鈕） |
| `.github/workflows/check-new-books.yml` | GitHub Actions 自動化設定 |
| `previous_books.json` | 上次檢查的書籍資料（自動產生） |
| `requirements.txt` | Python 依賴套件 |

---

## 環境變數說明

| 變數名稱 | 必填 | 說明 |
|---------|------|------|
| `SENDER_EMAIL` | 是 | 發送通知的 Gmail |
| `SENDER_PASSWORD` | 是 | Gmail 應用程式密碼 |
| `RECIPIENT_EMAIL` | 否 | 單一收件人（向下相容） |
| `GOOGLE_SHEETS_ID` | 否 | Google Sheets ID（訂閱功能） |
| `GOOGLE_CREDENTIALS_JSON` | 否 | Service Account JSON（訂閱功能） |
