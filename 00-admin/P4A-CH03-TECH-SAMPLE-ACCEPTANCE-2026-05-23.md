# P4A 驗收報告：第 03 講技術深度樣板章

日期：2026-05-23

## 1. 目標

本輪目標是將 `01-current/03-攝影師作品集.md` 修成技術深度樣板章，回應「新版教材需要更明確回到網頁設計本體」的要求。

第 03 講用來展示：

- GitHub 與 repository 的角色
- commit 與版本紀錄
- Vercel deployment 與 production 網站
- 自動重新部署
- 自訂網域與 DNS
- 圖片路徑、RWD、SEO、手機版驗收
- 常見部署錯誤排查

## 2. 修改檔案

- `01-current/03-攝影師作品集.md`
- `01-current/README.md`
- `01-current/MANIFEST.md`

## 3. 樣板章規格

第 03 講已改為六段式結構：

1. 破冰案例
2. 業態需求
3. 網頁設計重點
4. 功能與資料模型
5. AI 協作實作
6. 上線與延伸

本章與第 01 講的分工：

- 第 01 講：全書語氣與六段式架構樣板
- 第 03 講：技術深度與工程流程樣板

## 4. 技術內容補強

本輪回收 legacy 第 03 講的技術素材，並重新整理成正式教材語氣。

已補強內容：

- 攝影師作品集與 IG 的角色差異
- GitHub / Vercel 角色分工
- repository / commit / branch / deployment / production / domain / DNS 名詞
- 最小檔案結構：`index.html`、`images/`、`README.md`
- AI prompt 中要求語意化 HTML、RWD、SEO、alt 文字、真實內容約束
- GitHub commit message 範例
- Vercel 自動部署流程
- 自訂網域設定流程
- 常見錯誤排查表
- 手機版、SEO、技術與內容檢查清單

## 5. 契約檔同步

`01-current/README.md` 已新增第 03 講作為「技術深度樣板章」的定位。

`01-current/MANIFEST.md` 已將第 03 講狀態更新為「待老師確認」，備註為 P4A 技術深度樣板章已完成。

## 6. 驗證結果

結構檢查：

```text
01-current/03-攝影師作品集.md 僅有六個二級標題：
1. 破冰案例
2. 業態需求
3. 網頁設計重點
4. 功能與資料模型
5. AI 協作實作
6. 上線與延伸
```

Build 檢查：

```text
python3 build-book-v2.py
Reading lectures from: 01-current
Found 18 chapters
Written: book-preview-v2.html
Size: 454.4 KB
```

Preview 檢查：

- `book-preview-v2.html` 已包含第 03 講新版標題
- TOC 仍維持 18 講
- 第 03 講新版內容已進入 preview
- preview 中可搜尋到 `repository`、`Vercel deployment`、`DNS` 等技術關鍵詞

## 7. 未做事項

- 未修改第 02 講或第 04–18 講正文
- 未修改 legacy 檔案
- 未修改 build script
- 未新增 manifest-driven parser
- 未替工程團隊撰寫第 11 講正文

## 8. 下一輪建議

建議先讓 Cruz 檢查第 01 講與第 03 講兩個樣章：

1. 第 01 講是否可作為全書語氣樣板
2. 第 03 講是否足以展示技術教學深度
3. 是否需要再做一章功能型樣章，例如第 11 講民宿訂房網站

若第 03 講方向通過，再把「技術深度樣板」推廣到其他有明確技術副標題的章節。
