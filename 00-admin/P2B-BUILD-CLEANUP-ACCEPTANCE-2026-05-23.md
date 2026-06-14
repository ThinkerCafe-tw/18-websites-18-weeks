# P2B — Build Pipeline 命名清理驗收

日期：2026-05-23

## 一、處理原因

P2A 已讓新版 builder 可讀 `01-current/`，但根目錄仍同時存在：

- `build-book-v2.py`
- `book-preview-v2.html`
- `build-book.py`
- `book-preview.html`
- `fact-check.py`
- `VERIFICATION.html`

這些檔案會讓後續施工者誤以為仍存在 v1 / v2 雙軌。P2B 目標是清掉根目錄干擾，建立單一 active build 入口。

## 二、檔案移動

| 原位置 | 新位置 | 狀態 |
|---|---|---|
| `build-book-v2.py` | `04-build/scripts/build-book.py` | active builder |
| `book-preview-v2.html` | `04-build/previews/book-preview.html` | active preview |
| `build-book.py` | `04-build/scripts/legacy/build-book-legacy.py` | legacy reference |
| `fact-check.py` | `04-build/scripts/legacy/fact-check-legacy.py` | legacy reference |
| `book-preview.html` | `04-build/previews/legacy/book-preview-legacy.html` | legacy reference |
| `VERIFICATION.html` | `04-build/previews/legacy/VERIFICATION-legacy.html` | legacy reference |

## 三、Active command

```bash
python3 04-build/scripts/build-book.py
```

輸入：

- `01-current/`

輸出：

- `04-build/previews/book-preview.html`

## 四、驗收標準

- 根目錄不再出現 `build-book-v2.py` / `book-preview-v2.html`。
- 根目錄不再同時放置新舊 builder 與 preview。
- active builder 不再使用 `v2` 命名。
- active preview 固定輸出到 `04-build/previews/`。
- 舊檔案未刪除，改收進 legacy 區，保留歷史參考。

## 五、下一步

P6 可直接進入第 11 講「民宿訂房網站」全文修稿，不需要再先處理 build 命名問題。

## 六、驗證

```bash
python3 04-build/scripts/build-book.py
```

結果：

```text
Reading lectures from: /Users/sulaxd/Documents/18-websites-18-weeks/01-current
  Found 18 chapters
  Written: /Users/sulaxd/Documents/18-websites-18-weeks/04-build/previews/book-preview.html
  Size: 455.6 KB
```

根目錄掃描：

```bash
find . -maxdepth 1 -type f \( -name 'build-book*.py' -o -name 'book-preview*.html' -o -name 'fact-check.py' -o -name 'VERIFICATION.html' \) -print
```

結果：無輸出，代表根目錄已無 active/legacy build 殘留檔。
