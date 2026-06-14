# 第 12 講 overflow — 配套網站候選素材

> 來源：第12講 §5.2

把提示詞貼給 AI 之後，AI 會回傳一個完整的 HTML 檔案。首頁第一屏包含平台主張「先審核，再推薦」、數學、英文、國文、理化四個服務科目，以及「開始媒合」「先看媒合流程」兩個按鈕；往下依序是家長需求表、精選教師、媒合流程狀態條、審核說明、費用與保障與頁尾。教師照片先以免費圖庫的示意圖代替，AI 也用註解標出了日後要替換的正式檔名，例如 `images/tutor-01.jpg`。

> 來源：第12講 §5.2（HTML 骨架示意）

整體結構可以用下面的骨架示意（省略號代表實際內容，不是可直接貼用的程式碼），這就是頁面模組表落到程式碼後的樣子。其中「篩選與排序」被 AI 併進精選教師區塊、做成卡片上方的篩選列，是常見而可接受的合併：

```html
<header>…平台名稱與導覽…</header>
<main>
  <section class="hero">…平台主張、服務科目、開始媒合…</section>
  <section id="request">…家長需求表…</section>
  <section id="tutors">…篩選列與五張教師卡片…</section>
  <section id="process">…媒合流程狀態條…</section>
  <section id="verification">…身分驗證、學歷查核、試教回饋、推薦人…</section>
  <section id="fees">…媒合費、試教費、取消退款、替換老師…</section>
</main>
<footer>…聯絡信箱、服務地區、版權…</footer>
```

> 來源：第12講 §5.2（media query 節錄）

手機版的關鍵是 CSS 裡的 media query。AI 產出的規則節錄如下：

```css
/* 平板：教師卡片改為兩欄 */
@media (max-width: 1024px) {
  .tutor-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-bar { grid-template-columns: repeat(2, 1fr); }
}

/* 手機：全部單欄，header 改為直向排列，按鈕與欄位放大易點 */
@media (max-width: 640px) {
  .site-header { flex-direction: column; align-items: flex-start; }
  .site-nav { flex-wrap: wrap; gap: 12px; }
  .hero h1 { font-size: 1.5rem; }
  .tutor-grid, .form-grid, .filter-bar, .info-grid { grid-template-columns: 1fr; }
  .field-full { grid-column: auto; }
  .stepper { flex-direction: column; }
  .btn { display: block; width: 100%; text-align: center; }
  .hero-actions { flex-direction: column; }
}
```

用手機寬度打開同一個檔案，教師卡片會改成單欄，篩選欄位與按鈕也會放大成整排可點。
