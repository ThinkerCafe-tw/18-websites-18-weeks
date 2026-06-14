# 第 07 講 overflow — 配套網站候選素材

> 來源：第7講 §5.2 AI 產出結果（首屏描述與產出結構，正文已壓為定容版）

首頁第一屏包含店名、料理類型與一句話主張，以及「立即訂位」「查看菜單」兩個按鈕；頁首導覽列正下方有一條原型聲明，標示這是未串接正式後台的訂位原型，這正是提示詞收尾那句限制產生的效果。往下依序是菜單與低消、桌型說明、訂位選擇器、訂位表單、訂位規則、確認區與資料模型示意。照片先以免費圖庫的示意圖代替，AI 也用註解標出了日後要替換的正式檔名，例如 `images/hero.jpg`。

`header` 是店名與「菜單與低消、桌型說明、線上訂位、訂位規則」導覽；`main` 內依序是主視覺、菜單與低消、桌型說明、訂位選擇器、訂位表單、訂位規則、確認區、資料模型示意八個 `section`；`footer` 是示意地址、電話、Email、營業時間與版權聲明。

> 來源：第7講 §5.2 HTML 骨架示意

整體結構可以用下面的骨架示意（省略號代表實際內容，不是可直接貼用的程式碼），這就是表 7-1 的頁面模組落到程式碼後的樣子。其中資料模型示意是提示詞【資料模型】另外要求的展示區塊，不在表 7-1 的七個模組之內：

```html
<header>…店名與導覽…</header>
<main>
  <section class="hero">…店名、料理類型、主張、立即訂位…</section>
  <section id="menu">…招牌菜、套餐、低消與服務費…</section>
  <section id="tables">…二人桌、四人桌、包廂、吧台…</section>
  <section id="booking">…日期、人數、時段、可訂桌型與剩餘名額…</section>
  <section id="reserve-form">…姓名、手機、人數、特殊需求、兒童椅…</section>
  <section id="rules">…保留 10 分鐘、取消期限、未到處理、低消…</section>
  <section id="confirm">…訂位編號、日期、時段、人數、取消方式…</section>
  <section id="data-model">…五張資料表的示意卡片…</section>
</main>
<footer>…地址、電話、Email、版權…</footer>
```

> 來源：第7講 §5.2 互動示意細節

互動的部分，AI 用少量 JavaScript 做出提示詞要求的三個示意：選 2 位、4 位、6 位時，可訂桌型清單會跟著變，例如 6 位只會看到包廂與併桌建議；已額滿的「18:00 晚餐第一輪」按鈕是灰色且不可點；表單送出後，確認區會顯示「訂位已確認」、一組像 `SY-20260619-031` 的訂位編號與取消方式。

> 來源：第7講 §5.2 media query 節錄

手機版的關鍵是 CSS 裡的 media query。AI 產出的規則節錄如下：

```css
/* 平板：卡片改兩欄，主視覺改單欄 */
@media (max-width: 1024px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
  .hero { grid-template-columns: 1fr; }
}
/* 手機：全部單欄，頁首改直向排列，按鈕維持易點 */
@media (max-width: 640px) {
  .site-header { flex-direction: column; align-items: flex-start; }
  .grid, .form-grid { grid-template-columns: 1fr; }
  .hero h1 { font-size: 28px; }
  .btn { display: block; text-align: center; margin: 0 0 12px; }
  .btn.ghost { margin-left: 0; }
  .submit-btn { width: 100%; }
  .confirm-box dl { grid-template-columns: 1fr; }
}
```

用手機寬度打開同一個檔案，訂位選擇器與表單會改成單欄，額滿時段一樣是灰色不可點。
