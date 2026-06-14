# Build Pipeline 路徑遷移紀錄

> 狀態：**P2B 已收斂** · 2026-05-23

## 目前終態

active build 入口已固定為：

```bash
python3 04-build/scripts/build-book.py
```

輸入來源：

- `01-current/`

輸出位置：

- `04-build/previews/book-preview.html`

legacy build / 驗證檔已移入：

- `04-build/scripts/legacy/`
- `04-build/previews/legacy/`

## 原始問題

掃描結果：4 個 build/驗證檔仍寫死舊路徑 `01-教材內容/`，且舊路徑已不存在。

| 檔案 | 寫死位置 | 行為 |
|---|---|---|
| `build-book.py` | `INPUT_DIR = .../01-教材內容` (line 15) | 讀資料夾所有 `.md` |
| `build-book-v2.py` | `INPUT_DIR = .../01-教材內容` (line 15) | 過濾 `.endswith(".v2.md")` (line 320) |
| `fact-check.py` | `content_dir = .../01-教材內容` (line 217) | 掃 `.md`，docstring 也提到舊路徑 (lines 5–6, 213) |
| `VERIFICATION.html` | 19 講 hardcoded 表格指向 `01-教材內容/第NN講-XXX.md` (lines 213–231) | 純前端驗收儀表板 |

P2A 先修好新版 builder 的讀取來源，但根目錄仍殘留 `v2` 命名與舊 builder。P2B 已將 active builder 移入 `04-build/scripts/`，並將舊檔收進 legacy 區。

## 影響面

- **build-book.py**：跑舊 19 講路徑，**已過期**，應該指向 legacy 而非主稿
- **build-book-v2.py**：原本鎖 `.v2.md`，新版主稿剝掉 `.v2` 後篩選邏輯也失效
- **fact-check.py**：scope 不清，是要查正式稿還是 legacy？
- **VERIFICATION.html**：19 講儀表板與新版 18 講錯位，不能直接套

## 三條原始路線

### A. 最小遷移（建議）

只改 `build-book-v2.py` → `INPUT_DIR = 01-current`、移除 `.v2.md` 過濾，改為篩 `^\d{2}-.+\.md$` 且排除 `00-chapter-template.md` / `MANIFEST.md` / `README.md`。

- `build-book.py` 標記 deprecated，搬進 `04-build/scripts/legacy/`（產出 legacy 預覽用）
- `fact-check.py` 加 `--scope current|legacy` flag，default `current`
- `VERIFICATION.html` 重生成一份 18 講版本，舊的歸 legacy 區

成本：低 · 風險：低 · 立即可跑

P2A 已完成此路線的核心讀取邏輯；P2B 進一步移除 active 檔名中的 `v2`，並搬離根目錄。

### B. 雙軌並存

兩支 script 都活著、各自指向不同 INPUT_DIR；MANIFEST 成為「哪些已升級」的真相源。

- 適合修稿期：legacy 還要常翻、新版逐章 promote
- 風險：兩邊 drift，需要紀律
- 成本：中

### C. 完全 manifest-driven

build script 不掃資料夾、改讀 `MANIFEST.md` 表格 → 依「已定稿」狀態 include。

- 最乾淨、最對齊本次定錨精神
- 需要先寫 MANIFEST parser（YAML frontmatter 或固定 table 格式）
- 成本：高 · 風險：中（要先穩定 MANIFEST schema）

## 後續建議

**維持 A、預留 C**：

1. 目前先維持 `04-build/scripts/build-book.py` 作為唯一 active builder。
2. 等 18 講正文進入穩定期，再評估 C（MANIFEST schema 升級為 frontmatter / YAML sidecar）。
3. B 不建議當終態，僅作 A→C 過渡。

## 尚未處理

- 不改正文
- 不重生 18 講版 `VERIFICATION.html`
- 不重寫 legacy `fact-check.py`
- 不做 manifest-driven build parser
