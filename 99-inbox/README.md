# CTS × ROOM-CHAT-AI Inbox

兩個 Claude Code session 的協作信箱。

## 分工
- **CTS-版權策略 (surface:92)**: 教材文字 + 18個靜態HTML網站 + 書面截圖 → 學生學的東西
- **ROOM-CHAT-AI (surface:97)**: 變臉劇場 + Hitbox vibe coding + 後端API → 不學也能創業，學了變成 AI-based 網站

## 使用方式
- 寫入：`echo "消息" >> inbox/from-cts.md` 或 `inbox/from-room.md`
- 讀取：對方讀自己的收件檔
- 格式：`[時間] 來源: 消息`

## 檔案
- `from-cts.md` — CTS 寫給 ROOM 的
- `from-room.md` — ROOM 寫給 CTS 的
- `shared-state.md` — 共享狀態（兩邊都能讀寫）
