# P6 — 第 11 講功能型網站樣板章驗收

日期：2026-05-23

## 一、目標

依鄒老師回饋「期待功能型網站全文」，將第 11 講「民宿訂房網站」改寫為第一篇完整功能型網站樣板章。

本輪不交給工程團隊，原因是第 11 講仍屬內容判斷、語氣控制、商業敘事與技術深度整合，不是單純規格套版。

## 二、修改範圍

修改：

- `01-current/11-民宿訂房網站.md`
- `01-current/MANIFEST.md`

新增：

- `00-admin/P6-CH11-FUNCTIONAL-SAMPLE-ACCEPTANCE-2026-05-23.md`

取材：

- 原第 11 講 v2 主稿的 OTA、信任、心理學與警示內容
- `00-admin/P4B-CH11-HOMESTAY-TECH-BRIEF.md`
- legacy 第 12 講可回收概念：狀態機、日期選擇器、動態定價、取消階梯、併發衝突

## 三、新章節骨架

第 11 講已改為六段式：

1. 破冰案例
2. 業態需求
3. 網頁設計重點
4. 功能與資料模型
5. AI 協作實作
6. 上線與延伸

## 四、技術深度落點

已納入：

- 民宿官網與 OTA 的商業關係
- 單純表單與真正訂房系統的差異
- `RoomType` / `Room` / `Availability` / `Order` / `Payment` / `Guest`
- 房況狀態：可訂、保留中、已預訂、入住中、清潔中、封鎖、維修
- 訂單與付款狀態
- 付款成功頁與 webhook 的差異
- 後台模組：房況、訂單、價格、黑名單日期
- 動態定價：平日、週末、旺季、長住折扣
- AI 產出後常見錯誤與驗收清單

## 五、教材控制

已避免：

- 不要求學生真的串接金流
- 不收真實信用卡資料
- 不宣稱原型已可正式營運
- 不產生假評論、假證照或假媒體報導
- 不把 P4B brief 原樣貼成工程文件

## 六、MANIFEST

第 11 講狀態已從「待補技術內容」改為「待老師確認」。

備註已更新為：

```text
P6 功能型網站樣板章已完成；示範房型/房況/訂單/付款/後台與驗收清單
```

## 七、驗證

```bash
python3 04-build/scripts/build-book.py
```

結果：

```text
Reading lectures from: /Users/sulaxd/Documents/18-websites-18-weeks/01-current
  Found 18 chapters
  Written: /Users/sulaxd/Documents/18-websites-18-weeks/04-build/previews/book-preview.html
  Size: 461.6 KB
```

預覽內容檢查：

- `第 11 講：民宿訂房網站` 已出現在目錄與第 11 章正文。
- `RoomType`、`Webhook`、`房況` 等功能型網站關鍵詞已出現在預覽 HTML。
