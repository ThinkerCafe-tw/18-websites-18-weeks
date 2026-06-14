# 第 08 講 overflow — 配套網站候選素材

> 來源：第8講 §5.2（AI 產出結果 — 首屏完整描述與產出清單原文）

首頁第一屏左上是教室名稱、右上是導覽，主視覺放一句話主張「僵硬的身體，更歡迎來」，加上「預約第一堂體驗課」「查看本週課表」兩個按鈕，右側是教室空間的示意照片；往下依序是老師介紹、課程類型、本週課表、體驗課報名表單、候補說明與取消規則。照片先以免費圖庫的示意圖代替，AI 也用註解標出了日後要替換的正式檔名，例如 `images/studio-hero.jpg`。

這一版產出的內容可以整理成一份清單：

- 一個 `index.html`，HTML、CSS（Cascading Style Sheets，階層式樣式表）與 JavaScript 寫在同一個檔案內。
- `header`：教室名稱與導覽。
- `main` 內依序是主視覺、老師介紹、課程類型、本週課表、體驗課報名表單、候補說明、取消與扣堂規則七個 `section`。
- `footer`：Email、地址與版權聲明。
- `script` 內以六個資料物件示範 Teacher、ClassType、ClassSession、Enrollment、WaitlistEntry、StudentNote，課表上的名額與狀態就是由這些資料算出來的。

提示詞要求的互動示意也有做出來：課表裡名額為 0 的「陰瑜伽入門」，按鈕顯示為「加入候補」，送出候補後表單下方會顯示目前順位；在報名表單切換課程時，表單會同步顯示該堂課的老師、難度與剩餘名額。

> 來源：第8講 §5.2（AI 產出結果 — HTML 骨架示意）

整體結構可以用下面的骨架示意（省略號代表實際內容，不是可直接貼用的程式碼），這就是表 8-1 的頁面模組落到程式碼後的樣子。表 8-1 的七個模組各自落成一個區塊，頁尾則是 AI 自行補上的常見收尾：

```html
<header>…教室名稱與導覽…</header>
<main>
  <section class="hero">…教室名稱、主張、預約體驗課…</section>
  <section id="teachers">…老師介紹…</section>
  <section id="classes">…課程類型與難度…</section>
  <section id="schedule">…週課表、名額與報名按鈕…</section>
  <section id="signup">…體驗課報名表單…</section>
  <section id="waitlist">…候補順位與通知規則…</section>
  <section id="rules">…取消與扣堂規則…</section>
</main>
<footer>…Email、地址、版權…</footer>
```

> 來源：第8講 §5.2（AI 產出結果 — 手機版 media query 節錄）

手機版的關鍵是 CSS 裡的 media query。AI 產出的規則節錄如下：

```css
  /* 平板：老師與課程卡片改成兩欄 */
  @media (max-width: 1024px) {
    .grid { grid-template-columns: repeat(2, 1fr); }
    .hero { grid-template-columns: 1fr; }
  }
  /* 手機：全部單欄，課表改成直向卡片，按鈕放大成整排 */
  @media (max-width: 640px) {
    .site-header { flex-direction: column; gap: 10px; text-align: center; }
    .site-header nav a { margin: 0 8px; }
    .grid { grid-template-columns: 1fr; }
    .btn.ghost { margin-left: 0; margin-top: 12px; }
    .schedule-table thead { display: none; }
    .schedule-table tr { display: block; border: 1px solid var(--line); border-radius: 12px; margin-bottom: 14px; padding: 6px 14px; background: #fff; }
    .schedule-table td { display: flex; justify-content: space-between; gap: 12px; border: none; padding: 7px 0; }
    .schedule-table td::before { content: attr(data-label); color: var(--ink-soft); }
    .schedule-table td:last-child::before { display: none; }
    .schedule-table button, .signup-form .btn { width: 100%; }
  }
```

用手機寬度打開同一個檔案，課表會改成一張一張直向的課卡，欄位名稱在左、內容在右，按鈕放大成整排可點（見第 8 講圖 8-4）。

> 來源：第8講 §2.1（產業營運邏輯 — 場域多功能化的完整收入拆解）

非尖峰時段（平日上午十點到下午四點）變現的三個常見方向，可再展開細節：

- **租借給獨立老師**：身心靈工作坊或冥想課程的講師通常沒有固定場地，按場次租用瑜伽教室，是穩定的閒置時段填補。
- **商業攝影場地**：木質地板、柔和自然光的空間，是服飾、生活風格品牌拍攝偏好的場景，按時計費。
- **自辦主題活動**：「母女瑜伽日」「企業包班」「孕婦瑜伽工作坊」等週末主題場，客單價從單堂課四五百元跳到場次費一千元以上。

財務效果（業界觀察）：場地每坪產值可提升約四成；若再結合自有品牌周邊銷售（瑜伽墊、精油、教室聯名服飾），活動場次的客單價可再提升約兩成。關鍵在於這些收入全部建立在「已經付掉的固定場租」上，邊際成本極低，是教室從「服務業」走向「複合營運」的第二條腿。
