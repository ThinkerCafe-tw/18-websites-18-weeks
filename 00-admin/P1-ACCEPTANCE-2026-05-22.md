# P1 驗收報告 — 教材主稿工作流固化

- **日期**：2026-05-22
- **範圍**：工程層（資料夾結構 + 文件契約 + build path 評估）
- **正文動到了嗎**：❌ 沒有。本輪 0 字正文修改、0 段 legacy 合併、0 行內容刪除。

---

## 1. MANIFEST 是否能作為唯一施工入口？

**結論：可以。**

- `01-current/MANIFEST.md` 已具備：
  - 18 講主線索引表（講次/檔名/主題/v2 來源/legacy 對照/狀態/備註）
  - 狀態定義區塊（整理完成 / 待補技術內容 / 待人工修稿 / 待老師確認 / 已定稿）
  - 講次錯位對照（舊 19 → 新 18，美容院合一節點）
- 修稿人只需打開 MANIFEST：
  - 知道每一講當前狀態
  - 知道對應 legacy 在哪
  - 知道下一步該推到哪
- 不足（非阻塞）：MANIFEST 目前是純 Markdown table，未來若要被 build script 解析需升級為 frontmatter / YAML sidecar，路線見 `04-build/BUILD-MIGRATION.md` C 案。

---

## 2. README 補強

**已更新** `01-current/README.md`，新增四節：

- **一、正式稿規則**：檔名格式、內容骨架、範圍（18 + template + manifest + readme）
- **二、舊稿回收規則**：legacy 定位、回填要點（不整章、搬完更新 MANIFEST、不動 legacy 本體）
- **三、章節狀態規則**：5 個狀態 + 升級路徑表 + 備註欄要求
- **四、禁止事項**：不重寫正文、不 copy-paste 整章、不 `.v2`、不直接改 build path、不刪 legacy

頭部一行明示「施工入口 = MANIFEST.md」，避免從別處猜講次。

---

## 3. build-book-v2.py / book-preview-v2.html 評估

**結論：先提案、不動手。** 詳見 `04-build/BUILD-MIGRATION.md`。

掃描結果（4 個寫死舊路徑的檔案）：

| 檔案 | 行 | 問題 |
|---|---|---|
| `build-book.py` | L15 | `INPUT_DIR = 01-教材內容` — 已失效 |
| `build-book-v2.py` | L15 + L320 | INPUT_DIR 失效 + `.v2.md` 過濾也失效（新檔名剝掉 `.v2`） |
| `fact-check.py` | L5–6 / L213 / L217 | INPUT_DIR + docstring + argparse help 全寫死舊路徑 |
| `VERIFICATION.html` | L213–231 | 19 講 hardcoded 表格，與新版 18 講錯位 |

建議路線：**A 最小遷移**（改 INPUT_DIR + 篩選規則）→ 後續可升級 **C manifest-driven**。本輪不執行。

---

## 4. 正式稿區是否還有 .v2.md 或舊稿混入？

掃描指令與結果：

```
$ find . -name "*.v2.md" -not -path "./node_modules/*"
（無輸出）

$ ls 01-current/
00-chapter-template.md  README.md  MANIFEST.md
01-咖啡廳網站.md ... 18-總複習.md   (共 18 個講次檔)
```

- ✅ 全 repo `.v2.md` = 0 個
- ✅ `01-current/` 內僅有 18 講主稿 + 3 個契約檔（template/README/MANIFEST），無混入
- ✅ `02-legacy-materials/2025-original-19-lessons/` 19 個檔案完整、原檔名未動

---

## 5. P1 驗收標準對照

| 標準 | 結果 |
|---|---|
| 01-current 只有 18 講正式稿 + 契約檔 | ✅ |
| 正式稿檔名不含 .v2 | ✅ |
| 舊版 19 講完整保留在 legacy | ✅ |
| MANIFEST.md 能清楚看出 18 講主線 | ✅ |
| README.md 寫清正式稿規則、回收規則、狀態規則 | ✅（本輪補強） |
| 沒有舊稿與新版主稿混放 | ✅ |
| 沒有刪除教材內容 | ✅ |
| 沒有重寫正文 | ✅ |
| build script 評估方案產出 | ✅（`04-build/BUILD-MIGRATION.md`） |

---

## 6. 開放項（待 Cruz / 鄒老師決定，本輪不做）

- **BUILD-MIGRATION 路線拍板**（A / B / C） — 影響下一輪 build script 改動範圍
- **`course-outline.md`** 來源未指定，`00-admin/` 目前缺；可從 `.openclaw/course-outline.md` 拉進來（待確認）
- **`technical-recovery-notes.md`** 目前是空殼說明，修稿啟動後可逐章累積回收記錄
- **`04-build/scripts/` `04-build/previews/`** 目前空殼，等 BUILD-MIGRATION 拍板再搬

---

## 7. 沒做的事（依規格 + 安全邊界）

- ❌ 沒重寫任何正文
- ❌ 沒合併 legacy 技術段落
- ❌ 沒刪除任何檔案
- ❌ 沒改 build script（只評估）
- ❌ 沒搬根目錄其他散檔（`AGENTS.md`、`README*.md`、`memory/`、`websites/`、`screenshots/`、`__pycache__` 等規格未指明的）— 留給下輪
