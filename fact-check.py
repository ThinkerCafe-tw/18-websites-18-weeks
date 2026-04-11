#!/usr/bin/env python3
"""
事實查核腳本 — 掃描教材 .md 檔案中的可疑引用、精確數字、法律條文、繁簡混用。
用法：
  python3 fact-check.py                        # 掃描 01-教材內容/ 下所有 .md
  python3 fact-check.py --file 第01講-咖啡廳網站.md  # 只查單一檔案
Exit code: RED 存在 → 1, 僅 YELLOW → 0
"""

import argparse
import os
import re
import sys
from pathlib import Path

# ── 簡體字偵測（僅收錄有對應繁體異形字的簡化字） ──
# 每個字旁邊標注其繁體對應，確保不誤判繁簡同形字
SIMPLIFIED_CHARS = set(
    "这"  # 這
    "没"  # 沒
    "个"  # 個
    "们"  # 們
    "对"  # 對
    "会"  # 會
    "为"  # 為
    "关"  # 關
    "与"  # 與
    "学"  # 學
    "认"  # 認
    "设"  # 設
    "还"  # 還
    "应"  # 應
    "该"  # 該
    "让"  # 讓
    "说"  # 說
    "时"  # 時
    "机"  # 機
    "东"  # 東
    "种"  # 種
    "来"  # 來
    "进"  # 進
    "发"  # 發
    "现"  # 現
    "经"  # 經
    "过"  # 過
    "从"  # 從
    "给"  # 給
    "将"  # 將
    "开"  # 開
    "点"  # 點
    "问"  # 問
    "题"  # 題
    "习"  # 習
    "计"  # 計
    "际"  # 際
    "验"  # 驗
    "运"  # 運
    "动"  # 動
    "参"  # 參
    "数"  # 數
    "据"  # 據
    "规"  # 規
    "则"  # 則
    "国"  # 國
    "标"  # 標
    "准"  # 準
    "节"  # 節
    "页"  # 頁
    "链"  # 鏈
    "继"  # 繼
    "续"  # 續
    "环"  # 環
    "境"  # 境 (繁簡同形，移除)
    "变"  # 變
    "选"  # 選
    "择"  # 擇
    "请"  # 請
    "输"  # 輸
    "确"  # 確
    "证"  # 證
    "书"  # 書
    "签"  # 簽
    "处"  # 處
    "响"  # 響
    "独"  # 獨
    "创"  # 創
    "图"  # 圖
    "识"  # 識
    "别"  # 別 (繁簡同形，移除)
    "记"  # 記
    "录"  # 錄
    "显"  # 顯
    "读"  # 讀
    "写"  # 寫
    "删"  # 刪 (繁簡同形，移除)
    "号"  # 號
    "码"  # 碼
    "联"  # 聯
    "网"  # 網
    "络"  # 絡
    "视"  # 視
    "频"  # 頻
    "资"  # 資
    "讯"  # 訊
    "订"  # 訂
    "购"  # 購
    "买"  # 買
    "转"  # 轉
    "门"  # 門
    "导"  # 導
    "乐"  # 樂
    "区"  # 區
    "专"  # 專
    "业"  # 業
    "体"  # 體
    "长"  # 長
    "电"  # 電
    "话"  # 話
    "车"  # 車
    "馆"  # 館
    "医"  # 醫
    "院"  # 院 (繁簡同形，移除)
    "饭"  # 飯
    "店"  # 店 (繁簡同形，移除)
)
# 移除繁簡同形字（上面標注的）
SIMPLIFIED_CHARS -= set("境别删院店")

# ── 掃描規則 ──

def check_fake_citation(line: str, lineno: int, filename: str, results: list):
    """虛假引用模式"""
    patterns = [
        (r"根據.{1,30}(的|所發布的|發布的)?(報告|調查|研究|白皮書|藍皮書)", "可能不存在的報告引用"),
        (r".{2,20}(在\s*\d{4}\s*年\s*發布)", "引用特定年份發布的報告，需確認來源"),
        (r".{2,20}(統計|調查|數據)\s*(顯示|指出|表明)", "統計引用需確認來源"),
    ]
    for pat, msg in patterns:
        for m in re.finditer(pat, line):
            results.append(("RED", filename, lineno, m.group(0).strip(), msg))


def check_precise_numbers(line: str, lineno: int, filename: str, results: list):
    """可疑精確數字"""
    # 精確百分比（含小數）
    for m in re.finditer(r"\d+\.\d+\s*%", line):
        # 排除程式碼區塊中的百分比 (width: 100.0% 之類)
        context = line[max(0, m.start() - 10):m.end() + 10]
        if "width" not in context and "height" not in context:
            results.append(("YELLOW", filename, lineno, m.group(0).strip(), "精確百分比需確認來源"))

    # 精確倍數
    for m in re.finditer(r"(高出|增長|成長|提升|降低|減少|超過)\s*\d+\.?\d*\s*倍", line):
        results.append(("YELLOW", filename, lineno, m.group(0).strip(), "精確倍數需確認來源"))

    # 精確金額/市場規模
    for m in re.finditer(r"(市場規模|營收|產值|總額|價值)\s*[\d,.]+\s*(億|萬|兆)", line):
        results.append(("YELLOW", filename, lineno, m.group(0).strip(), "精確金額需確認來源"))

    # 精確秒數/時間
    for m in re.finditer(r"\d+\.\d+\s*秒", line):
        results.append(("YELLOW", filename, lineno, m.group(0).strip(), "精確數字需確認來源"))


def check_legal_refs(line: str, lineno: int, filename: str, results: list):
    """法律條文引用"""
    for m in re.finditer(r"第\s*\d+\s*(條|款|項|章|編)", line):
        results.append(("YELLOW", filename, lineno, m.group(0).strip(), "法律條文需法律專家確認"))


def check_simplified_chars(line: str, lineno: int, filename: str, results: list):
    """繁簡混用"""
    # 跳過程式碼區塊
    stripped = line.strip()
    if stripped.startswith("```") or stripped.startswith("`"):
        return
    for i, ch in enumerate(line):
        if ch in SIMPLIFIED_CHARS:
            # 取附近文字作為上下文
            start = max(0, i - 3)
            end = min(len(line), i + 4)
            context = line[start:end].strip()
            results.append(("YELLOW", filename, lineno, context, f"簡體字「{ch}」"))
            # 同一行只報一次
            return


def scan_file(filepath: Path) -> list:
    """掃描單一檔案，回傳 (level, filename, lineno, excerpt, message) list"""
    results = []
    filename = filepath.name
    in_code_block = False

    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            # 追蹤程式碼區塊
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            check_fake_citation(line, lineno, filename, results)
            check_precise_numbers(line, lineno, filename, results)
            check_legal_refs(line, lineno, filename, results)
            check_simplified_chars(line, lineno, filename, results)

    return results


def main():
    parser = argparse.ArgumentParser(description="教材事實查核")
    parser.add_argument("--file", "-f", help="只查單一檔案（相對於 01-教材內容/）")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    content_dir = script_dir / "01-教材內容"

    if not content_dir.exists():
        print(f"錯誤：找不到 {content_dir}", file=sys.stderr)
        sys.exit(2)

    if args.file:
        target = content_dir / args.file
        if not target.exists():
            print(f"錯誤：找不到 {target}", file=sys.stderr)
            sys.exit(2)
        files = [target]
    else:
        files = sorted(content_dir.glob("*.md"))

    all_results = []
    for f in files:
        all_results.extend(scan_file(f))

    # 輸出報告
    red_count = sum(1 for r in all_results if r[0] == "RED")
    yellow_count = sum(1 for r in all_results if r[0] == "YELLOW")

    print("=== 事實查核報告 ===")
    print(f"掃描檔案數：{len(files)}")
    print(f"發現問題：{len(all_results)} 個")
    print()

    for level, filename, lineno, excerpt, msg in all_results:
        # 從檔名取講次
        lecture = filename.replace(".md", "")
        print(f"[{level}] {lecture}:L{lineno} — 「{excerpt}」")
        print(f"  → {msg}")
        print()

    print(f"總計：RED={red_count} YELLOW={yellow_count}")

    if red_count > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
