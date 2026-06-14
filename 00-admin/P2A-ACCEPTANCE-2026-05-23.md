# P2A 驗收報告 — Build 最小遷移 + Course Outline 正規化

- **日期**：2026-05-23
- **路線**：BUILD-MIGRATION **A 案**（最小遷移）
- **正文動到了嗎**：❌ 沒有。0 字正文修改、0 段 legacy 合併、0 個檔案刪除。

---

## 1. 修改檔案清單

### 變更（2 個檔）

| 檔案 | 變更 | 行 |
|---|---|---|
| `build-book-v2.py` | `INPUT_DIR` 從 `01-教材內容` → `01-current` | 15 |
| `build-book-v2.py` | 新增 `NON_CHAPTER_FILES` set + `CHAPTER_PATTERN` regex | 17–19 |
| `build-book-v2.py` | `gather_chapters()` 篩選邏輯：原 `.endswith(".v2.md")` → `CHAPTER_PATTERN.match(f) and f not in NON_CHAPTER_FILES` | ~325 |
| `build-book-v2.py` | docstring 更新（移除「19 markdown lecture files」說明） | 1–6 |

### 新增（1 個檔）

| 檔案 | 來源 | 備註 |
|---|---|---|
| `00-admin/course-outline.md` | 複製自 `.openclaw/course-outline.md` | 頭部加 HTML comment 註明來源 + 複製時間 + SNAPSHOT 性質 |

### 原檔保留未動

- `.openclaw/course-outline.md` — 原檔完整保留（48 行），未刪除、未動內容

### 刻意不動（最小必要 + 不需誤觸）

- `build-book.py`：原本指向舊 19 講路徑，已自然失效，不會被誤跑；保留現狀
- `fact-check.py`：同上，本輪不修
- `VERIFICATION.html`：純前端 19 講儀表板與新版錯位，本輪不修
- `book-preview.html`：build-book.py 產物，本輪不再生
- 規格未指明的根目錄散檔（`AGENTS.md` / `README.md` / `memory/` / `screenshots/` / `websites/` 等）

---

## 2. Build / Preview 測試結果

```
$ python3 build-book-v2.py
Reading lectures from: /Users/sulaxd/Documents/18-websites-18-weeks/01-current
  Found 18 chapters
  Written: /Users/sulaxd/Documents/18-websites-18-weeks/book-preview-v2.html
  Size: 463.5 KB
  Opened in browser.
```

- ✅ 章節數正確：18（與 MANIFEST 一致）
- ✅ INPUT_DIR 指向 `01-current/`
- ✅ 不再依賴 `.v2.md` 字尾
- ✅ 不讀 legacy（`02-legacy-materials/` 未被掃描）
- ✅ 契約檔（`00-chapter-template.md` / `MANIFEST.md` / `README.md`）被正確排除
- ✅ HTML 產物大小 463.5 KB，與遷移前同數量級
- ✅ 內含 19 個 `chapter-` id 標記（18 章 + 目錄章節索引）

---

## 3. 舊路徑 hardcode 殘留掃描

掃描 `01-教材內容` 與 `.v2.md` 兩個關鍵字（排除 .openclaw / node_modules / memory）：

### 仍含舊路徑、但本輪刻意不動（依「最小必要」原則）

| 檔案 | 性質 | 是否會誤跑 |
|---|---|---|
| `build-book.py` | 舊 19 講 builder | ❌ 不會（路徑失效自然 fail） |
| `fact-check.py` | 舊 fact-check script | ❌ 不會（路徑失效自然 fail） |
| `VERIFICATION.html` | 舊 19 講儀表板 | ❌ 純靜態頁、不影響 build |

### 仍含舊名稱、但屬於歷史文件 / 不是執行路徑

- `01-current/MANIFEST.md` — 表格本來就要列「來源 v2 檔案」，這是必要的對照
- `01-current/README.md` — 禁止事項條列「不要 .v2.md」，是規則本身
- `04-build/BUILD-MIGRATION.md` — 提案文件、引用舊路徑作為現況描述
- `00-admin/P1-ACCEPTANCE-2026-05-22.md` — 驗收報告，引用舊路徑為歷史證據
- `preview-issues.md` / `99-inbox/*` / `Claude.md` / `.claude-v2/v2-writing-guide.md` — 歷史筆記、AI 工作日誌

### 不再有 hardcode 影響正式 build pipeline

`build-book-v2.py` 是新版主稿的唯一 builder，其路徑與篩選邏輯已全部遷移完成。

---

## 4. Course Outline 正規化驗收

| 標準 | 結果 |
|---|---|
| 複製到 `00-admin/course-outline.md` | ✅（55 行 = 48 原文 + 7 行 SNAPSHOT 標頭） |
| 原檔 `.openclaw/course-outline.md` 保留 | ✅（48 行未動） |
| 新檔頭部標註來源 | ✅（HTML comment：來源 / 複製時間 / SNAPSHOT 性質 / 同步要求） |

新檔頭部標註：

```
<!--
來源：.openclaw/course-outline.md（原檔保留、未動）
複製時間：2026-05-23
用途：00-admin 集中存放管理層文件，供 build/manifest 參考
本檔為 SNAPSHOT；後續若 .openclaw/ 原檔更新，需手動同步至此
-->
```

---

## 5. 規格對照驗收

| 規格 | 結果 |
|---|---|
| 1. 新版 build / preview 改讀 01-current/ | ✅ |
| 2. 不再依賴 .v2.md 檔名 | ✅（改 regex 篩 `NN-題目.md`） |
| 3. 不讀 legacy | ✅（INPUT_DIR 不含 legacy 路徑） |
| 4. 不改正文內容 | ✅（0 字修改） |
| 5. 不做 manifest-driven parser | ✅（仍走 filesystem scan） |
| 6. 不做雙軌 v1/v2 系統 | ✅（build-book.py 自然失效、未維持） |
| 7. course-outline 複製到 00-admin、原檔保留、標註來源 | ✅ |

禁止事項全數遵守：

- ❌ 不重寫教材正文
- ❌ 不合併 legacy 內容
- ❌ 不刪除原始資料
- ❌ 不把 MANIFEST 變成複雜 schema

---

## 6. 開放項（下一輪可選）

- **build-book.py / fact-check.py 處置**：建議下一輪標 deprecated 或搬進 `04-build/scripts/legacy/`，避免新人誤跑
- **VERIFICATION.html 重生**：18 講版需重新做，舊版歸 legacy 區
- **course-outline 同步機制**：目前是手動 SNAPSHOT，若 `.openclaw/` 原檔更新頻繁，可加 hash check
- **build 產物搬遷**：`book-preview-v2.html` 目前仍生在根目錄，下一輪可移到 `04-build/previews/`
