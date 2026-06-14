# 第 02 講 overflow — 配套網站候選素材

> 來源：第2講 §5.2

## AI 產出的健身房單頁網站：完整骨架示意

整體結構可以用下面的骨架示意（省略號代表實際內容，不是可直接貼用的程式碼），這就是表 2-1 的頁面模組落到程式碼後的樣子。表 2-1 的六個模組之外，AI 把體驗預約表單獨立成第七個區塊，是常見而可接受的拆分：

```html
<header>…場館名稱與導覽…</header>
<main>
  <section class="hero">…名稱、定位、主張、預約首次體驗…</section>
  <section id="coaches">…教練姓名、證照、專長、適合族群…</section>
  <section id="plans">…月繳、年繳、私教、入會費…</section>
  <section id="trial">…預約、報到、器材介紹、不強迫推銷承諾…</section>
  <section id="space">…器材、尖峰提醒、更衣室、女性專屬區…</section>
  <section id="refund">…月繳、年繳、終止規則、客服窗口…</section>
  <section id="booking">…體驗預約表單…</section>
</main>
<footer>…營業時間、Email、服務地區、版權…</footer>
```

> 來源：第2講 §5.2

## RWD 的關鍵：media query 規則節錄

手機版的關鍵是 CSS 裡的 media query。AI 產出的規則節錄如下：

```css
/* 平板：教練、方案與空間照片改為兩欄 */
@media (max-width: 1024px) {
  .grid, .plans { grid-template-columns: repeat(2, 1fr); }
}
/* 手機：全部單欄，header 直向排列，按鈕與表單欄位維持易點 */
@media (max-width: 640px) {
  header { flex-direction: column; align-items: flex-start; gap: 0.4rem; }
  header nav a { margin-left: 0; margin-right: 1rem; }
  section { padding: 3rem 5vw; }
  .hero { padding: 4rem 5vw; }
  h1 { font-size: 1.6rem; }
  .grid, .plans, .space-grid { grid-template-columns: 1fr; }
  .steps { flex-direction: column; }
  .btn { display: block; margin: 0.5rem auto; max-width: 280px; }
}
```

平板斷點（1024px）把教練、方案與空間照片改成兩欄；手機斷點（640px）把所有格線改成單欄、header 改直向排列、按鈕放大成整排可點。用手機寬度打開同一個 `index.html`，課程方案會改成單欄呈現。

> 來源：第2講 §5.2

## 首屏與各區塊的完整描述

首頁第一屏包含場館名稱、地區與定位、一句話主張，以及「預約首次體驗」「查看課程方案」兩個按鈕；往下依序是教練團隊、課程方案、首次體驗流程、空間與設備、退費與合約、體驗預約表單與頁尾。照片先以免費圖庫的示意圖代替，AI 也用註解標出了日後要替換的正式檔名，例如 `images/coach-lin.jpg`。

各區塊的完整內容：

- `header`：場館名稱與導覽。
- `main` 內依序是主視覺、教練團隊（三位教練的照片、證照、專長與適合對象）、課程方案（月繳、年繳、私教課包與入會費說明）、首次體驗流程（含不強迫推銷承諾，以及保留給真實學員見證的區塊）、空間與設備（含尖峰時段提醒與女性專屬區）、退費與合約、體驗預約表單七個 `section`。
- `footer`：營業時間、Email、服務地區與版權聲明。

把產出結果對回第 2 講第 2 節的業態需求：首頁第一屏的定位與主張回應「誰敢走進來」；透明的方案價格與退費合約區塊回應「合約綁架」的恐懼；器材介紹與不強迫推銷承諾回應「能力不足」的恐懼與「教練干擾」的猶豫；尖峰時段提醒與女性專屬區回應「擁擠」與「隱私分區」的猶豫；保留給真實學員見證的區塊回應「多元體態的真實見證」——AI 沒有自己編造學員評價，正好符合提示詞「請避免假評價」的要求（教練資歷與價格則為示意佔位，程式碼註解已標明須替換為真實資料）。每個區塊都應該能對回一個需求；對不回去的區塊，就是可以刪掉的裝飾。
