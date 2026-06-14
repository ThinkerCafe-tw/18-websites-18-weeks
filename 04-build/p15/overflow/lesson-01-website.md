# 第 01 講 overflow — 配套網站候選素材

> 來源：第1講 §5.2

## AI 產出首頁的首屏內容描述（圖 1-2 對照文）

首頁第一屏包含店名、地點與特色、一句話定位，以及「查看菜單」「導航前往」兩個按鈕；往下依序是關於我們、菜單、空間與設備、營業資訊、聯絡與頁尾。照片先以免費圖庫的示意圖代替，AI 也用註解標出了日後要替換的正式檔名與建議拍攝內容，例如 `images/hero.jpg`。

> 來源：第1講 §5.2

## HTML 骨架示意

整體結構可以用下面的骨架示意（省略號代表實際內容，不是可直接貼用的程式碼），這就是第 01 講表 1-6 的頁面區塊落到程式碼後的樣子。表 1-6 沒有列出的 header 與 footer，是 AI 補上的導覽與頁尾，屬於常見而可接受的補充：

```html
<header>…店名與導覽…</header>
<main>
  <section class="hero">…店名、定位、查看菜單、導航前往…</section>
  <section id="about">…品牌故事…</section>
  <section id="menu">…咖啡、非咖啡、甜點與價格…</section>
  <section id="space">…插座、Wi-Fi、座位、限時規則…</section>
  <section id="info">…地址、電話、營業時間、公休日…</section>
  <section id="contact">…Instagram、LINE、電話…</section>
</main>
<footer>…地址、電話、版權…</footer>
```

> 來源：第1講 §5.2

## 響應式 media query 節錄

手機版的關鍵是 CSS 裡的 media query。AI 產出的規則節錄如下：

```css
/* 平板：菜單與空間設備改為兩欄 */
@media (max-width: 1024px) {
  .menu-grid, .space-grid { grid-template-columns: repeat(2, 1fr); }
}
/* 手機：全部單欄，按鈕、地址與電話維持易點 */
@media (max-width: 640px) {
  .menu-grid, .space-grid { grid-template-columns: 1fr; }
}
```

平板寬度（1024px 以下）時菜單與空間設備改為兩欄；手機寬度（640px 以下）時全部單欄，按鈕、地址與電話維持易點。
