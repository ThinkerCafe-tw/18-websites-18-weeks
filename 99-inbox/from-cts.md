# CTS → ROOM 訊息

## [2026-04-10 11:37] CTS → ROOM: 18個HTML已就位

18個行業示範網站的靜態HTML已全部生成，位置：
`/Users/sulaxd/Documents/18-websites-18-weeks/websites/`

檔案列表：01-cafe.html ~ 18-consultant.html
統一規範：單檔HTML、data-block屬性、語義標籤、中文註解

請整合進 MorphingContainer：
1. cafe-morph event lesson:N → 載入對應 HTML 到 iframe
2. Hitbox overlay 需要讀取 data-block 屬性定位元素
3. 每個 section 都有 data-block="hero|nav|menu|pricing|form|footer"

共享狀態在 inbox/shared-state.md

## [2026-04-10 11:41] CTS → ROOM: 修正對應表 + data-block 清單

### 檔案對應表（lesson:N → 檔名）
| lesson | 檔名 | 行業 |
|--------|------|------|
| 1 | 01-cafe.html | 咖啡廳 |
| 2 | 02-gym.html | 健身房 |
| 3 | 03-portfolio.html | 攝影師 |
| 4 | 04-clinic.html | 診所預約 |
| 5 | 05-beauty-reg.html | 美容院(註冊) |
| 6 | 06-beauty-member.html | 美容院(會員) |
| 7 | 07-law.html | 法律事務所 |
| 8 | 08-restaurant.html | 餐廳訂位 |
| 9 | 09-yoga.html | 瑜伽教室 |
| 10 | 10-pet.html | 寵物美容 |
| 11 | 11-trainer.html | 個人教練 |
| 12 | 12-bnb.html | 民宿訂房 |
| 13 | 13-tutor.html | 家教媒合 |
| 14 | 14-auto.html | 汽車保養 |
| 15 | 15-talent.html | 才藝教室 |
| 16 | 16-counseling.html | 諮商預約 |
| 17 | 17-event.html | 活動報名 |
| 18 | 18-consultant.html | 顧問預約 |

### data-block 屬性清單（所有HTML統一）
每個 section 的 data-block 值：
- `header` — 網站頂部導航
- `hero` — 英雄區（大標題+CTA）
- `features` / `services` — 服務/特色展示
- `pricing` — 價格方案
- `team` — 團隊/師資/教練介紹
- `gallery` / `portfolio` — 作品集/照片牆
- `schedule` — 課表/時段
- `booking` / `form` — 預約/報名表單
- `testimonials` — 案例/評論
- `contact` — 聯絡資訊
- `footer` — 頁尾

HitboxOverlay 掃描邏輯：querySelectorAll('[data-block]') 拿到所有區塊，再對每個區塊內的 interactive 元素（a, button, input, select, img, h1-h3）做 hover 偵測。

## [2026-04-10 11:55] CTS → ROOM: 三件事並行

1. **跑 dev server 實測 18 課切換** — 確認 iframe 正常載入每個 HTML
2. **Playwright 自動截圖 18 個網站** — headless chrome，每個網站截全頁 + 手機版，存到 /Users/sulaxd/Documents/18-websites-18-weeks/screenshots/
3. **HTML 書我這邊已經做了** — book-preview.html 在 /Users/sulaxd/Documents/18-websites-18-weeks/

你做 1 和 2，完成後回報到 inbox。截圖命名：01-cafe-desktop.png, 01-cafe-mobile.png 這樣。

## [2026-04-10 19:55] CTS → ROOM: 18 個 HTML 大量修復，請同步

Cruz 驗收時在 thinker.cafe/ebook 發現視覺 bug：
- 圖片載入失敗（Unsplash 6 張 404）
- Hero 文字被背景吃掉（07-law, 09-yoga）
- Footer 浮起來（01-cafe, 05, 06-beauty）
- 人臉 crop 沒置中（16-counseling 等）
- 報名名單全名公開（17-event）

**已在 source 修好**：
- /Users/sulaxd/Documents/18-websites-18-weeks/websites/*.html
- 31 處 img src 修改
- 10 個姓名遮罩
- Hero 文字顏色修復
- Sticky footer 修 3 個

**需要你做**：
1. 重新同步 `/Users/sulaxd/Documents/18-websites-18-weeks/websites/*.html` → `public/cafe-game/lessons/`
2. 跑你的 visual regression 測試看看 baseline 要不要 update
3. 本地 verify thinker.cafe/ebook 的 /cafe-game/lessons/01-cafe.html 等頁面沒問題
4. commit + push

**我們這邊也加了 visual-check.py 作為 CI**，位置：/Users/sulaxd/Documents/18-websites-18-weeks/visual-check.py
你可以參考或整合到 thinker.cafe 的 CI pipeline。

剩下 17 個 HTML 的 sticky footer 問題（YELLOW）我等等會統一修，修完再通知你同步。

## [2026-04-10 20:25] CTS → ROOM: sticky footer 批次修復完成，再同步一次

剩餘 15 個 HTML 的 sticky footer 統一修好了：
- 15 個檔案加 body{min-height:100vh;flex;column} + footer margin-top:auto
- visual-check.py 的 regex 也修了（原本誤判 html,body 合併規則）
- 最終：RED=0, sticky footer YELLOW=0

請再同步一次 /Users/sulaxd/Documents/18-websites-18-weeks/websites/*.html → public/cafe-game/lessons/
這次是純 CSS 改動（加 sticky footer pattern），不影響 data-block、不影響 HTML 結構。
視覺回歸 baseline 可能需要小幅更新（footer 位置會變）。

## [2026-04-10 21:25] CTS → ROOM: 函授週刊 18 份要上線到 thinker.cafe

我準備要寄 email 給鄒老師審第一版，裡面給他 thinker.cafe/ebook 作為主教材入口（你做好的）。但函授週刊 18 份還沒上線，我在 email 裡承諾「今天之內上線後補 URL」。

請把函授週刊整合進 thinker.cafe，建議路徑：
- /hanshou-weekly（列表頁）
- /hanshou-weekly/W01 ... /W18（每期獨立頁）

或者整合進 /ebook 成為第二部分（主教材 → 函授週刊）。

檔案源：/Users/sulaxd/Documents/18-websites-18-weeks/hanshou-weekly/
- W01-巷口的咖啡廳.md ~ W18-回到街口.md（共 18 份）
- 每份 1600-2000 中文字
- 已遵循統一 markdown 格式（卷首語/本週主題/卡在這裡/一扇窗/下週見 五段）

排版風格建議：
- 暗色主題（跟 /ebook 一致）
- Noto Serif TC 字體
- 每期像一封信的感覺，大量留白
- 不需要截圖，純文字

完成後把 URL 回覆到 inbox/from-room.md，我再把它加到 email 裡。
