# P4B — 第 11 講「民宿訂房網站」技術拆解 Brief

- **日期**：2026-05-23
- **目的**：為第 11 講後續修稿備料，集中梳理訂房系統的技術骨架（業態、頁面、資料、狀態、金流、後台），供修稿時局部回收。
- **正文動到了嗎**：❌ 沒有。本文件僅 brief、未動 `01-current/11-民宿訂房網站.md` 一字、未合併 legacy。
- **取材範圍**：v2 主稿（business / psychology 強）+ legacy 第 12 講（state machine / pricing 強）+ 業界一般實踐。
- **使用方式**：修稿者讀完整章後，按本 brief 的 §1–6 補充技術骨架，§7 索引指向 legacy 可回收段落，§8 為修稿排版建議。

---

## 1. 民宿訂房網站核心需求

### 1.1 商業層（why）

| 需求 | 內容 | 出處 |
|---|---|---|
| 抽成漏洞 | OTA（Booking/Airbnb/Agoda）抽 15–20%，加上促銷再讓 10–20% | v2 §11-3、legacy §12-1 |
| 自有轉化 | 把 OTA 客導回官網直訂，第二次起省抽成 | v2 §11-6、legacy §12-2 三 |
| 雙邊市場 | 民宿是房東 ↔ 旅客雙邊，與單邊（咖啡廳/教練）邏輯不同 | legacy §12-2 一 |
| 隱形佣金 | 在地行程退佣 15–20%，旺季可達房費規模 | v2 §11-3 心法三 |

### 1.2 旅客層（what user feels）

- **首圖 50ms 判斷**（Lindgaard 2006）— 決定下一張的開關
- **三大恐懼**：照騙、安全/隱私、後勤支援
- **三大猶豫**：付款流程現代感、取消政策友善度、地圖最後一哩
- **三大信任觸發**：主人敘事、含缺點的真實評論、在地隱藏地圖

### 1.3 系統層（what site must do）

- 即時房況查詢（多日期跨度）
- 防超賣（同房同日不可重複訂）
- 線上付款（取代「匯款後傳簡訊」）
- 取消/退款規則
- 房東後台（房況、訂單、價格、黑名單）

---

## 2. 頁面與功能模組

按旅客動線排列：

| # | 頁面 | 模組 | 關鍵元素 |
|---|---|---|---|
| 1 | 首頁 | 主視覺 / 生活主張 / 房價概覽 / 直訂優惠 banner | 早晨光氛圍首圖、一句話定位 |
| 2 | 空間故事 | 主人是誰 / 為何在這裡 / 早餐食材來源 | 三句真實、有溫度 |
| 3 | 房型列表 | 房型卡片（主圖+副圖+人數+價格區間+獨特賣點） | 至少 2 房型、設施按功能分組 |
| 4 | 房型詳情 | 主圖 + 4–5 副圖 + 設施分類清單 + 價格日曆 | 設施分睡眠/衛浴/餐飲/休閒四類 |
| 5 | 訂房流程 | 日期選擇器 → 人數 → 加購 → 旅客資料 → 付款 → 確認 | 內含 hold-15min 機制 |
| 6 | 在地指南 | 3–5 個推薦點、藏 spot、餐廳路線 | 旅客「我是這裡的人」心理 |
| 7 | 交通指引 | 開車路線、搭車路線、最後一哩照片路標 | 夜晚抵達不焦慮 |
| 8 | 常見問答 | 5 題：入住時間、停車、早餐、寵物、退費 | 直接回應三大恐懼 |
| 9 | 付款結果 | 成功頁（含入住指引）/ 失敗頁（含重試入口） | webhook 結果回顯 |
| 10 | 訂單查詢 | 旅客憑 email + 訂單號查狀態 / 申請取消 | 無需註冊登入 |

**後台**（房東端，§6 詳述）：房況管理、訂單管理、價格管理、黑名單日期。

---

## 3. 資料模型

最小可行 schema（命名僅示意、修稿時可調整為老師偏好用語）。

### 3.1 RoomType（房型）

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | string | 房型 ID |
| name | string | 例：檜木雙人房 |
| max_guests | int | 最大入住人數（大人+兒童分計） |
| size_ping | int | 坪數 |
| amenities | json | 設施分類：{sleep, bath, food, leisure} |
| photos | array<url> | 1 主圖 + 4–5 副圖 |
| base_price_weekday | int | 平日基準價 |
| base_price_weekend | int | 週末基準價 |
| description | text | 獨特賣點敘事 |

### 3.2 Room（房間個體）

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | string | 房間 ID |
| room_type_id | string | 對應房型 |
| label | string | 顯示名（例：201 號房） |
| active | bool | 是否上架 |

> 同房型可能有多間實體房間，需要分開管理避免超賣。

### 3.3 Availability（日期房況）

| 欄位 | 型別 | 說明 |
|---|---|---|
| room_id | string | 房間 |
| date | date | 入住日（單日一筆） |
| status | enum | available / held / booked / blocked / cleaning / maintenance |
| held_until | datetime? | 保留中時的鎖定到期時間 |
| order_id | string? | 對應訂單（held / booked 狀態必填） |
| price_override | int? | 該日特殊定價（旺季/促銷） |

> 設計選擇：以「每房每日一筆」為粒度，可避免跨日期區間查詢的複雜度。

### 3.4 Order（訂單）

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | string | 訂單號 |
| room_id | string | 房間 |
| check_in | date | 入住日 |
| check_out | date | 退房日 |
| guest_count | int | 人數 |
| guest_name | string | 主訂房人 |
| guest_email | string | 聯絡 email |
| guest_phone | string | 聯絡電話 |
| status | enum | pending / confirmed / cancelled / refunded / no_show / completed |
| total_amount | int | 房費 + 加購總額 |
| created_at | datetime | 建立時間 |
| confirmed_at | datetime? | 付款成功時間 |
| cancelled_at | datetime? | 取消時間 |
| refund_amount | int? | 已退金額 |
| notes | text? | 旅客備註 |

### 3.5 Payment（付款記錄）

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | string | 付款 ID |
| order_id | string | 訂單 |
| provider | string | 例：藍新 / 綠界 / Stripe |
| provider_txn_id | string | 金流方交易號 |
| amount | int | 金額 |
| status | enum | initiated / success / failed / refunded |
| webhook_received_at | datetime? | webhook 回傳時間 |
| raw_payload | json | 金流方原始回傳 |

### 3.6 Guest（旅客）— 選用

可不獨立、嵌在 Order 內。若要做回頭客行銷再抽出來：

| 欄位 | 型別 | 說明 |
|---|---|---|
| email | string (PK) | 主鍵 |
| name | string | — |
| phone | string | — |
| visit_count | int | 入住次數 |
| last_stay | date | 最後入住日 |
| marketing_opt_in | bool | 訂閱同意 |

---

## 4. 狀態流程

### 4.1 房間日期狀態機（Availability.status）

```
                     ┌──────────┐
                     │ blocked  │  ← 房東手動鎖（黑名單日）
                     └──────────┘
                          ↑↓ (admin)
   ┌──────────┐  hold   ┌──────────┐  pay   ┌──────────┐
   │available │ ──────→ │  held    │ ─────→ │  booked  │
   └──────────┘         └──────────┘        └──────────┘
        ↑                    │ timeout/cancel       │ check_in
        │                    │                       ↓
        │                    ↓                  ┌──────────┐
        │              (back to available)      │ in_stay  │
        │                                       └──────────┘
        │                                            │ check_out
        │                                            ↓
        │              clean done            ┌──────────┐
        └────────────────────────────────── │ cleaning │
                                             └──────────┘
                                                  │ maintenance?
                                                  ↓
                                            ┌──────────┐
                                            │maintain..│
                                            └──────────┘
```

**轉換規則（節點清單）**：

| 從 | 到 | 觸發 | 備註 |
|---|---|---|---|
| available | held | 旅客送出訂房表單 | 鎖 15 分鐘 |
| held | available | 15 分鐘未付款 | 自動退回 |
| held | available | 旅客主動放棄 | — |
| held | booked | webhook 收到付款成功 | 訂單 confirmed |
| booked | cancelled | 取消申請（按 §5 退費規則） | refund 走金流方 |
| booked | in_stay | check_in 當日 00:00 | 排程或入住時改 |
| in_stay | cleaning | check_out 當日 12:00 | — |
| cleaning | available | 清潔完成 | 房東手動或排程 |
| any | blocked / maintenance | 房東手動 | 黑名單日 / 設備維修 |

**鐵律**：同一 `(room_id, date)` 只能有一個 status。寫入時需 DB-level 唯一索引 + 樂觀鎖（version 欄）或 row-level 鎖。

### 4.2 訂單狀態機（Order.status）

```
pending ─→ confirmed ─→ completed
   │           │
   │           └──→ cancelled ──→ refunded
   └──→ cancelled (timeout, never paid)
```

---

## 5. 金流流程

### 5.1 付款頁

- 進入條件：Availability 已從 available 切到 held、Order 已建（status=pending）
- 顯示：訂單摘要（房型/日期/人數/金額）、付款方式選項、倒數計時器（15:00 起跳）
- 動作：選擇付款方式 → redirect 到金流方 hosted page，或顯示金流方 SDK iframe

### 5.2 付款成功

```
旅客付款 → 金流方 → redirect 旅客回 /payment/return
                ↘
                 webhook → /payment/webhook (主信源)
```

- **單一信源原則**：以 webhook 為準，return page 僅作為旅客 UX 反饋
- 收到 webhook 後：
  1. 驗證簽章 / 比對 provider_txn_id
  2. Order.status: pending → confirmed
  3. Availability.status: held → booked（多日期一起翻）
  4. 寄訂房確認信 + 入住指引
  5. Payment.status: initiated → success

### 5.3 付款失敗

- 來源：webhook 回失敗 或 return page 帶失敗碼
- 動作：
  1. Payment.status: initiated → failed
  2. Order 維持 pending（保留 15 分鐘窗口讓旅客重試）
  3. 15 分鐘到、仍 pending → 視為放棄、Availability 釋放
- UI：提供「再試一次」入口、不要直接把 Order 砍掉

### 5.4 Webhook / 通知概念

| 通知 | 對象 | 觸發 | 內容 |
|---|---|---|---|
| 訂房成功 | 旅客（email） | Order confirmed | 訂單摘要 + 入住指引 PDF + 取消連結 |
| 訂房成功 | 房東（LINE/Email） | Order confirmed | 新訂單通知 |
| 入住前提醒 | 旅客（email/SMS） | check_in − 1 天 | 天氣、交通、check-in 時間 |
| 退房後評價邀請 | 旅客（email） | check_out + 24h | 評分連結（v2 §11-2 真實評論機制） |
| 取消確認 | 旅客 + 房東 | Order cancelled | 退款金額 + 預計到帳日 |
| 黑名單變更 | 房東後台 | admin 手動 | — |

### 5.5 取消退款

採彈性階梯（legacy §12-4 四）：

| 距入住日 | 退款比例 | 設計理由 |
|---|---|---|
| ≥ 30 天 | 100% | 計畫初期、給旅客信心 |
| 14–30 天 | 75% | 開始機會成本 |
| 7–14 天 | 50% | 進一步壓縮隨意取消 |
| < 3 天 | 0% | 房東已無重新出租時間 |

> 修稿建議：v2 主稿目前提及「損失規避」但未給具體階梯，可從這裡補。

---

## 6. 後台需求

### 6.1 房況管理（Availability admin）

- 日曆檢視（月 / 週 / 房間軸）
- 點任一日 → 改 status（鎖定 blocked / 解鎖 / 標 maintenance）
- 批次操作：選範圍 + 一鍵鎖（春節、農曆年、私人用）

### 6.2 訂單管理（Order admin）

- 列表：依狀態過濾（pending / confirmed / cancelled）
- 詳情：旅客資料、付款記錄、可手動退款 / 標 no_show
- 匯出：CSV 月結

### 6.3 價格管理（Pricing admin）

- 房型基準價：平日 / 週末
- 季節區間：日期範圍 + 加價百分比（例：春節 +100%）
- 連住折扣：≥ 3 晚 -5%、≥ 7 晚 -15%
- **天花板 / 地板**：強制設定每房型最高/最低價，避免動態定價失控（legacy §12-4 三）
- 提示：所有規則必須房東一眼看懂，禁黑箱演算法

### 6.4 黑名單日期（Blocked dates）

- 用途：私人使用、設備保養、節慶不接客
- 操作：日曆選範圍 → 一鍵 blocked
- 與動態定價解耦：blocked 日不顯示價格、不可訂

### 6.5 後台 UX 守則（修稿時可引用）

- 房東是非技術人，UI 要像 Google Calendar 而非 admin panel
- 取消政策最多 3 層、每層一句話
- 不要讓房東配「公式」、給「設定」即可

---

## 7. Legacy 舊稿可回收段落索引

來源：`02-legacy-materials/2025-original-19-lessons/第12講-民宿訂房網站.md`

| Legacy 段落 | 行 | 主題 | 為何值得回收 | 回收形式 |
|---|---|---|---|---|
| §12-1 投資報酬率 | 26–30 | 自有訂房 ROI 計算（5–15 萬建置、第一年回本） | v2 沒給具體 ROI 數字、CTA 力道弱 | 短段補入 v2 §11-6（OTA 抽成對照後） |
| §12-2 雙邊市場 | 36–40 | 房東/旅客需求對立、平台是信任中介 | v2 跳過商業結構直入心法 | 概念句、不整段搬，補在 v2 §11-3 開頭 |
| §12-2 平台依賴四陷阱 | 42–44 | 佣金階梯 / 評價綁架 / 數據隔絕 / 定價干預 | 強化 v2 §11-3 心法一的「為何要切斷依賴」 | 4 點 bullet 補入 |
| §12-3 狀態機交通燈 | 54–70 | 房間狀態機完整類比 + 超賣防呆原理 | v2 完全沒談技術骨架；本講「L5 動手」需要這層支撐 | 修稿主推此段、改寫成教材語氣補入 v2 §11-6 前 |
| §12-4 一 房型展示 3 個常見 AI 錯誤 | 76–84 | 照片無層次 / 設施流水帳 / 價格不透明 | v2 §11-6 提示詞缺「AI 輸出後常見問題」 | 3 點 bullet 補入「步驟四：只改三件事」之後 |
| §12-4 二 日期選擇器 4 項功能 | 86–92 | 灰掉已訂日 / 價格直顯 / 退房日範圍 / 連住折扣 | v2 完全沒提日期選擇器 UX | 補入 §11-6 步驟四或新增「步驟五：日期選擇器」 |
| §12-4 三 動態定價四層 | 94–100 | 平日 / 週末 / 旺季 / 長住四層 + 天花板地板 | v2 沒給價格設計骨架 | 表格補入 §11-6，搭 §6.3 |
| §12-4 四 彈性階梯取消政策 | 102–106 | 30/14/7/3 天四層退款比例 | v2 §11-2 提到取消政策心理成本但沒給具體階梯 | 表格補入 §11-2 末 |
| §12-5 一 假評論問題 | 112–118 | 公平交易法、AI 假評論辨識 | v2 §11-5 警示二相關但角度不同 | 不重複搬、修稿者擇一 |
| §12-5 二 照騙問題 | 120–124 | 廣角誇大、後製界線 | v2 §11-2 恐懼一已有但 legacy 給了實作建議 | 補「照片後製界線」一句 |
| §12-5 三 定價失控 | 126–130 | 線性加價陷阱、條款不可三層以上 | 修稿時與 §6.3 / §5.5 配套引用 | 提示詞 guard 段 |
| §12 重要名詞 | 148–158 | 狀態機 / 雙邊市場 / 動態定價 / 彈性取消 / 併發衝突 | v2 已有「重要名詞」但缺技術詞 | 補 3 詞：狀態機、雙邊市場、併發衝突 |

**回收禁忌**：

- 不整段搬，挑句改寫成 v2 語氣（口語、有節奏、半口頭半書面）
- 不搬 legacy 標題格式（v2 用 `### 11-N` + 副標、legacy 用 `## 12-N`）
- 不搬 legacy 中段標題（「**一、二、三**」），v2 用無編號小標 + bullet

---

## 8. 第 11 講正式修稿建議

修稿者讀本 brief 後，可按以下順序動正文（修稿時段、本 brief 不動）：

### 8.1 結構診斷

v2 現況：
- ✅ L1 產業聆聽（恐懼 / 猶豫 / 信任）— 強
- ✅ L2 心法（OTA / 變動成本 / 隱形佣金）— 強
- ✅ L3 心理學（50ms / 社會證明 / 損失規避）— 強
- ✅ L4 警示三種黑暗手法 — 強
- ⚠️ L5 動手（vibe coding）— 偏「提示詞 + 步驟四」，**缺技術骨架**
- ❌ 無資料模型、無狀態機、無金流流程、無後台 — **本講最大缺口**

### 8.2 建議改動範圍

**改正文時建議：限 §11-6（L5 動手）內補強，其他段落不動。**

具體補強落點：

1. **§11-6 開頭**：補一段「為什麼民宿訂房比咖啡廳/教練網站難」— 引狀態機與雙邊市場概念，從 §1.1 與 §4.1 抽 3–5 句
2. **§11-6 提示詞之後**：補「AI 輸出後 3 個常見問題」（照片無層次 / 設施流水帳 / 價格不透明），從 §7 legacy §12-4 一
3. **新增步驟五（建議）**：「日期選擇器要有的四件事」— 從 §7 legacy §12-4 二
4. **新增步驟六（建議）**：「動態定價：四層架構與天花板」— 從 §7 legacy §12-4 三 + §6.3
5. **§11-2 末尾**：補「彈性階梯取消政策」四層表格 — 從 §5.5
6. **重要名詞區**：補三詞（狀態機、雙邊市場、併發衝突）— 從 §7 legacy §12 重要名詞

### 8.3 修稿節奏

依 MANIFEST 狀態：第 11 講目前「待補技術內容」。建議路徑：

```
待補技術內容 → 待人工修稿 → 待老師確認 → 已定稿
   (本 brief)     (按 8.2 局部補)  (鄒老師看)
```

每階段升級需在 MANIFEST 備註欄寫一行說明。

### 8.4 不要做的事

- ❌ 不重寫 v2 任何段落（v2 是樣板章 01 的妹妹章、語氣已對齊）
- ❌ 不把 legacy 第 12 講整章搬進來
- ❌ 不把資料模型表格原樣貼進正文（教材不是技術文檔；表格只進「重要名詞」或必要範例）
- ❌ 不引用本 brief 的標題編號（§1.1 等）— 本 brief 是內部備料、不對外
- ❌ 不改 build script、不改 MANIFEST schema、不刪 legacy

---

## 9. 文件守則

- 本 brief 屬 `00-admin/` 管理層文件、非教材
- 修稿完成後不需刪除，作為後續其他講次（10 個人教練 / 12 家教媒合 等同樣含交易流的講）的對照基準
- 若 v2 主稿日後升級，本 brief 不需同步更新（snapshot 性質）
