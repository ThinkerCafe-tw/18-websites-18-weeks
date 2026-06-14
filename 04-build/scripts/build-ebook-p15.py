#!/usr/bin/env python3
"""
Build the P15 二校修訂模擬版 ebook (HTML + PDF) for 鄒老師校稿.

Two-document layout (textbook convention):
  front.pdf  cover + 序 + 目錄, roman folios at bottom center, cover unnumbered
  body.pdf   18 lectures, page 1 starts at 第 1 講, mirrored running heads
             (even: 「頁碼　網頁設計」 / odd: 「第Ｎ章　章名　頁碼」)
  merged     front + body via pypdf

TOC page numbers are real: the body document is rendered once to collect
anchor -> page mappings, then the TOC is generated with literal numbers.

- Reuses build-book.py's md->HTML converter and chapter gathering.
- Replaces （圖檔：`fig-*.png`，隨稿附件） pointer paragraphs with embedded
  images from 04-build/p15/figures/ (pointer kept when the file is missing).
- 表題在表上、圖題在圖下（截圖類）.

Usage: DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib \
       python3 04-build/scripts/build-ebook-p15.py
"""

import datetime
import html
import importlib.util
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
FIG_DIR = os.path.join(ROOT_DIR, "04-build", "p15", "figures")
PREFACE_MD = os.path.join(ROOT_DIR, "04-build", "p15", "preface.md")
DIFF_JSON = os.path.join(ROOT_DIR, "04-build", "p15", "revision-diff.json")
PREVIEW_DIR = os.path.join(ROOT_DIR, "04-build", "previews")


def revision_guide_block():
    """本版修訂對照表 — 老師拿龍虎紙本逐章對照用。"""
    import json

    if not os.path.exists(DIFF_JSON):
        return ""
    with open(DIFF_JSON, encoding="utf-8") as fh:
        chs = json.load(fh)["chapters"]
    rows = []
    for c in chs:
        delta = c["new"] - c["old"]
        sign = f"+{delta}" if delta >= 0 else str(delta)
        rows.append(
            f'<tr><td class="rg-ch">第{int(c["nn"])}章<br>{html.escape(c["name"])}</td>'
            f'<td class="rg-wc">{c["old"]:,}<br>↓<br>{c["new"]:,}<br>'
            f'<span class="rg-delta">({sign})</span></td>'
            f'<td class="rg-hint">{html.escape(c["hint"])}</td></tr>'
        )
    intro = (
        "<p class=\"rg-intro\">這版是您手上龍虎二校紙本的<strong>修訂模擬版</strong>，"
        "章名與書眉與紙本一致（「第 N 章」），可逐章對照；下表「校稿提示」欄指引您翻到紙本對應位置看新增了什麼。"
        "全書並依空院教材規範收進每章七千字內（128,872 → 119,013 字），精簡的技術深度另行保留，可後續安排於函授週刊課業輔導。</p>"
    )
    return (
        '<div class="page revguide">'
        '<h2>本版修訂對照表</h2>'
        f"{intro}"
        '<table class="rg-table"><thead><tr>'
        '<th>章次</th><th>字數<br>紙本→本版</th><th>主要修訂與校稿提示</th>'
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )

DATE = datetime.date.today().isoformat()
EDITION = "二校修訂模擬版"

_spec = importlib.util.spec_from_file_location(
    "build_book", os.path.join(SCRIPT_DIR, "build-book.py")
)
bb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bb)

POINTER_RE = re.compile(
    r"<p>（圖檔：<code[^>]*>(fig-[^<]+?)</code>，隨稿附件）</p>"
)
CAPTION_RE = re.compile(r"<p><strong>(表|圖) ")
# 教科書慣例：表題在表上、圖題在圖下 — 截圖的圖題移到圖後
FIGSWAP_RE = re.compile(
    r'(<p class="caption"><strong>圖 [^<]*</strong>[^<]*</p>)\s*'
    r'(<div class="figure[^>]*>.*?</div>)',
    re.S,
)

CN_NUM = [
    "", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八",
]


def running_head(idx: int, title: str) -> str:
    name = re.sub(r"^第\s*\d+\s*講[：:]\s*", "", title).strip()
    return f"第{CN_NUM[idx]}章　{name}"


def embed_figures(chapter_html: str) -> str:
    def repl(m):
        fname = m.group(1)
        if not os.path.exists(os.path.join(FIG_DIR, fname)):
            return m.group(0)
        cls = "fig-mobile" if "mobile" in fname else "fig-desktop"
        return (
            f'<div class="figure {cls}">'
            f'<img src="{html.escape(f"../p15/figures/{fname}")}" '
            f'alt="{html.escape(fname)}"></div>'
        )

    return POINTER_RE.sub(repl, chapter_html)


def add_section_ids(body: str, idx: int):
    secs = []

    def repl(m):
        text = m.group(1)
        sid = f"chapter-{idx}-s{len(secs) + 1}"
        secs.append((sid, re.sub(r"<[^>]+>", "", text)))
        return f'<h2 id="{sid}">{text}</h2>'

    # converter 給 h2 的 id 跨章重複（例如每章都有 1-破冰案例），整顆換成唯一 id
    return re.sub(r"<h2[^>]*>(.*?)</h2>", repl, body), secs


COMMON_CSS = r"""
:root {
  --font-mono: 'SF Mono', 'Menlo', 'Songti TC', 'Source Han Serif TC',
    'Noto Serif CJK TC', monospace; /* CJK fallback 防 tofu */
  --font-hei: 'PingFang TC', 'Noto Sans CJK TC', 'Heiti TC', sans-serif;
}
.page { page-break-after: always; }
.page::after { content: none; } /* 螢幕版角標，紙本版式用書眉/書腳頁碼 */

body { font-size: 10.5pt; line-height: 1.75; color: #000; }
p { text-indent: 2em; margin: 0.15em 0; orphans: 2; widows: 2; }
p.caption, .figure p, li p, blockquote p { text-indent: 0; }
strong { color: #000; }

.chapter h1, h2, h3, h4, h5 { font-family: var(--font-hei); color: #000; }
.chapter h1 { border-bottom: none; font-size: 18pt; }
h2 { font-size: 14pt; }
h3 { font-size: 12pt; }
h4 { font-style: normal; }
h2, h3 { page-break-after: avoid; }

p.caption { margin: 0.8em 0 0.3em; }

table { font-size: 9.5pt; }
table th, table td { border: 0.6pt solid #444; }
table thead th { background: #f0f0f0; }
table tbody tr:nth-child(even) td { background: transparent; }
table tr { page-break-inside: avoid; }

.figure { text-align: center; margin: 10pt 0 4pt; text-indent: 0; }
.figure img { border: 0.5pt solid #c8c8c8; }
.fig-desktop img { max-width: 100%; }
.fig-mobile img { max-width: 56mm; }

pre { white-space: pre-wrap; word-break: break-word; }
"""

FRONT_CSS = r"""
@page {
  size: A4;
  margin: 24mm 20mm 22mm 20mm;
  @bottom-center {
    content: counter(page, lower-roman);
    font-family: 'Songti TC', serif;
    font-size: 9pt;
    color: #333;
  }
}
@page blank {
  @bottom-center { content: none; }
}
.cover { page: blank; }
.cover .masthead {
  font-family: var(--font-hei);
  font-size: 12pt;
  line-height: 1.7;
  color: #222;
  margin-bottom: 2.4em;
}
.cover .masthead-course { font-size: 13pt; font-weight: bold; }
.cover h1 { font-size: 23pt; letter-spacing: 0.05em; white-space: nowrap; }
.cover .edition-note { font-size: 9pt; color: #555; }
.edition-banner {
  text-align: center;
  margin-top: 18pt;
  font-size: 11pt;
  color: #8a3b12;
}
.preface h2 { text-align: center; font-family: var(--font-hei); }

/* 目錄：兩級條目 + 點線導引 + 真實頁碼 */
.toc h2 { text-align: center; font-family: var(--font-hei); }
.toc-body { margin-top: 1.5em; }
.toc-body p { text-indent: 0; margin: 0.3em 0; }
.toc-body a { color: #000; text-decoration: none; display: flex; align-items: baseline; }
.toc-body .dots {
  flex: 1 1 auto;
  border-bottom: 0.6pt dotted #666;
  margin: 0 0.4em 0.28em;
  min-width: 2em;
}
.toc-ch { font-family: var(--font-hei); font-weight: bold; margin-top: 0.9em !important; }
.toc-sec { padding-left: 2em; font-size: 10pt; }
.toc-front a::after { content: none; }
.toc-front a { display: inline; }

/* 修訂對照表 */
.revguide h2 { text-align: center; font-family: var(--font-hei); }
.rg-intro { font-size: 10pt; line-height: 1.7; margin: 1em 0 1.4em; text-indent: 0; }
.rg-table { width: 100%; border-collapse: collapse; font-size: 8.6pt; line-height: 1.5; }
.rg-table th, .rg-table td { border: 0.6pt solid #555; padding: 4pt 5pt; vertical-align: top; }
.rg-table thead th { background: #ececec; font-family: var(--font-hei); text-align: center; }
.rg-table tr { page-break-inside: avoid; }
.rg-ch { font-family: var(--font-hei); white-space: nowrap; text-align: center; width: 12%; }
.rg-wc { text-align: center; white-space: nowrap; width: 13%; font-variant-numeric: tabular-nums; }
.rg-delta { color: #8a3b12; font-size: 8pt; }
.rg-hint { width: 75%; }
"""

BODY_CSS = r"""
@page {
  size: A4;
  margin: 24mm 20mm 22mm 20mm;
}
@page :left {
  @top-left {
    content: counter(page) "　　網頁設計";
    font-family: 'Songti TC', serif;
    font-size: 9pt;
    color: #333;
  }
}
@page :right {
  @top-right {
    content: string(chap) "　　" counter(page);
    font-family: 'Songti TC', serif;
    font-size: 9pt;
    color: #333;
  }
}
.chap-marker {
  string-set: chap content();
  display: block;
  height: 0;
  font-size: 0;
  line-height: 0;
  overflow: hidden;
}
/* 校稿 PDF：章換新頁即可，不強制右頁起（避免螢幕上出現空白左頁；實體書左右頁由排版處理） */
.chapter { page-break-before: always; }
.chapter:first-child { page-break-before: auto; }
"""


def html_shell(title: str, css: str, body: str) -> str:
    return (
        f'<!DOCTYPE html>\n<html lang="zh-TW">\n<head>\n<meta charset="UTF-8">\n'
        f"<title>{html.escape(title)}</title>\n<style>\n{bb.CSS}\n{COMMON_CSS}\n{css}\n</style>\n"
        f"</head>\n<body>\n{body}\n</body>\n</html>\n"
    )


def to_roman(n: int) -> str:
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def build():
    from weasyprint import HTML
    from pypdf import PdfReader, PdfWriter

    chapters = bb.gather_chapters()
    print(f"chapters: {len(chapters)}")

    chapter_blocks = []
    toc_struct = []  # (anchor, title, is_section)
    for ch in chapters:
        body = embed_figures(ch["html"])
        body = CAPTION_RE.sub(r'<p class="caption"><strong>\1 ', body)
        body = FIGSWAP_RE.sub(r"\2\n\1", body)
        body, secs = add_section_ids(body, ch["idx"])
        marker = html.escape(running_head(ch["idx"], ch["title"]))
        chapter_blocks.append(
            f'<div class="page chapter" id="{ch["id"]}">\n'
            f'<span class="chap-marker">{marker}</span>\n{body}\n</div>'
        )
        toc_struct.append((ch["id"], ch["title"], False))
        toc_struct.extend((sid, text, True) for sid, text in secs)

    body_html = html_shell(
        f"{bb.BOOK_TITLE}（正文）", BODY_CSS, "".join(chapter_blocks)
    )
    body_path = os.path.join(PREVIEW_DIR, f"ebook-p15-{DATE}-body.html")
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    with open(body_path, "w", encoding="utf-8") as fh:
        fh.write(body_html)

    # Pass 1: render body, collect anchor -> page (1-based)
    body_doc = HTML(body_path, base_url=body_path).render()
    anchor_page = {}
    for pno, page in enumerate(body_doc.pages, 1):
        for name in page.anchors:
            anchor_page.setdefault(name, pno)
    print(f"body pages: {len(body_doc.pages)}")

    # Front matter: cover + 序 + 目錄 (with literal page numbers)
    preface_block = ""
    preface_toc = ""
    if os.path.exists(PREFACE_MD):
        with open(PREFACE_MD, "r", encoding="utf-8") as fh:
            preface_html = bb.md_to_html(fh.read(), source_name="preface.md")
        preface_block = f'<div class="page preface">\n{preface_html}\n</div>'
        preface_toc = '<p class="toc-ch toc-front"><a><span>序</span></a></p>'
        print("preface: embedded")
    else:
        print("preface: MISSING (skipped)")

    toc_items = [
        '<p class="toc-ch toc-front"><a><span>本版修訂對照表</span></a></p>',
        preface_toc,
    ]
    for anchor, title, is_sec in toc_struct:
        pno = anchor_page.get(anchor, 0)
        cls = "toc-sec" if is_sec else "toc-ch"
        toc_items.append(
            f'<p class="{cls}"><a><span>{html.escape(title)}</span>'
            f'<span class="dots"></span><span>{pno}</span></a></p>'
        )

    front_body = f"""
<div class="page cover">
  <div class="masthead">
    國立臺北商業大學附設空中進修學院<br>
    國立臺中科技大學附設空中進修學院<br>
    <span class="masthead-course">115 學年度上學期　專科部「網頁設計」教材</span>
  </div>
  <h1>{bb.BOOK_TITLE}</h1>
  <div class="ornament"></div>
  <div class="subtitle">{bb.BOOK_SUBTITLE}</div>
  <div class="authors">編著者：{bb.BOOK_AUTHORS}</div>
  <div class="year">2026</div>
  <div class="edition-banner">{EDITION}<br>{DATE}・供校稿使用<br><span class="edition-note">（本版即您手上龍虎二校紙本之修訂模擬版，封面與內容對照見次頁「修訂對照表」）</span></div>
</div>
{revision_guide_block()}
{preface_block}
<div class="page toc">
  <h2>目 錄</h2>
  <div class="toc-body">
    {''.join(toc_items)}
  </div>
</div>
"""
    front_html = html_shell(f"{bb.BOOK_TITLE}（前置）", FRONT_CSS, front_body)
    front_path = os.path.join(PREVIEW_DIR, f"ebook-p15-{DATE}-front.html")
    with open(front_path, "w", encoding="utf-8") as fh:
        fh.write(front_html)

    front_pdf = os.path.join(PREVIEW_DIR, f"ebook-p15-{DATE}-front.pdf")
    body_pdf = os.path.join(PREVIEW_DIR, f"ebook-p15-{DATE}-body.pdf")
    HTML(front_path, base_url=front_path).write_pdf(front_pdf)
    body_doc.write_pdf(body_pdf)

    # Merge
    writer = PdfWriter()
    for part in (front_pdf, body_pdf):
        for pg in PdfReader(part).pages:
            writer.add_page(pg)
    # 固定輸出檔名：原地更新同一份，校稿者不必每次重開
    out_pdf = os.path.join(PREVIEW_DIR, "網頁設計-校稿版.pdf")
    with open(out_pdf, "wb") as fh:
        writer.write(fh)
    for tmp in (front_pdf, body_pdf):
        os.remove(tmp)
    print(f"PDF:  {out_pdf} ({os.path.getsize(out_pdf)/1024/1024:.1f} MB)")


if __name__ == "__main__":
    build()
