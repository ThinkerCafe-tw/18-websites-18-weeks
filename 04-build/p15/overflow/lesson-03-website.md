# 第 03 講 overflow — 配套網站候選素材

> 來源：第3講 §5.2

AI 產出首頁的完整首屏描述（正文已壓縮）：

首頁第一屏包含攝影師名稱、地區與服務類型、一句話主張，以及「看作品」「詢問檔期」兩個按鈕；往下依序是作品分類、服務方案、拍攝流程、關於我、詢問表單與頁尾。照片先以免費圖庫的示意圖代替，AI 也用註解標出了日後要替換的正式檔名，例如 `images/wedding-01.jpg`。作品分類為婚紗、婚禮紀錄、形象照三類，每類各 4 張示意圖與案例說明。其中表 3-5 的案例說明被 AI 併進作品分類區塊，是常見而可接受的合併。

> 來源：第3講 §5.2

整體結構的 HTML 骨架示意（省略號代表實際內容，不是可直接貼用的程式碼），這就是表 3-5 的頁面區塊落到程式碼後的樣子：

```html
<header>…攝影師名稱與導覽…</header>
<main>
  <section class="hero">…名稱、主張、看作品、詢問檔期…</section>
  <section id="works">…三類作品、示意圖與案例說明…</section>
  <section id="plans">…方案、價格區間、交件時間、加選規則…</section>
  <section id="process">…詢問、溝通、拍攝、精修、交件…</section>
  <section id="about">…攝影師介紹…</section>
  <section id="contact">…詢問表單…</section>
</main>
<footer>…Email、Instagram、服務地區、版權…</footer>
```

> 來源：第3講 §5.2

手機版的關鍵是 CSS 裡的 media query。AI 產出的規則節錄如下：

```css
/* 平板：作品集兩欄 */
@media (max-width: 1024px) {
  .grid, .plans { grid-template-columns: repeat(2, 1fr); }
}
/* 手機：全部單欄，按鈕與表單欄位維持易點 */
@media (max-width: 640px) {
  .grid, .plans { grid-template-columns: 1fr; }
}
```

用手機寬度打開同一個檔案，作品集會改成單欄，按鈕也會放大成整排可點。
