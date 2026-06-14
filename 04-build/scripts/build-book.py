#!/usr/bin/env python3
"""
Build a single-HTML book preview from 01-current/ (18 lecture files).
Usage: python3 04-build/scripts/build-book.py
Output: 04-build/previews/book-preview.html.
"""

import os
import re
import html
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
INPUT_DIR = os.path.join(ROOT_DIR, "01-current")
PREVIEW_DIR = os.path.join(ROOT_DIR, "04-build", "previews")
OUTPUT_FILE = os.path.join(PREVIEW_DIR, "book-preview.html")

# Files in 01-current/ that are contracts, not lecture chapters.
NON_CHAPTER_FILES = {"00-chapter-template.md", "MANIFEST.md", "README.md"}
# Chapter filename pattern: NN-題目.md  (NN = 01..18)
CHAPTER_PATTERN = re.compile(r"^\d{2}-.+\.md$")

BOOK_TITLE = "AI 時代個人網站開發實戰"
BOOK_SUBTITLE = "從需求訪談到系統上線：18 週完整實戰"
BOOK_AUTHORS = "鄒慶士、湯明軒"


# ---------------------------------------------------------------------------
# Markdown -> HTML converter (no external deps)
# ---------------------------------------------------------------------------

def md_to_html(text: str, source_name: str = "") -> str:
    """Convert a subset of markdown to HTML.

    Supports: ATX headings, fenced code blocks, horizontal rules, unordered
    lists (- * ◆), ordered lists (1. 2. ...), GFM tables, screenshot
    placeholders ([截圖: desc] / [截圖：desc]), inline code, bold, links.
    """
    lines = text.split("\n")
    out = []
    in_code = False
    in_ul = False  # bullet list state
    in_ol = False  # ordered list state
    i = 0

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def is_table_separator(s: str) -> bool:
        """Match a GFM separator row like '|---|---|' or '---|---|---'
        (with or without outer pipes, and optional alignment colons)."""
        if not s:
            return False
        # Must contain at least one pipe and only dashes/pipes/colons/spaces
        if "|" not in s:
            return False
        if not re.match(r'^[\s\|\-:]+$', s):
            return False
        # Must have at least 3 dashes somewhere
        return bool(re.search(r'-{3,}', s))

    while i < len(lines):
        raw = lines[i]

        # --- Code blocks ---
        if raw.strip().startswith("```"):
            close_lists()
            if not in_code:
                in_code = True
                out.append('<pre><code>')
            else:
                in_code = False
                out.append('</code></pre>')
            i += 1
            continue

        if in_code:
            out.append(html.escape(raw))
            i += 1
            continue

        stripped = raw.strip()

        # --- Blank line ---
        if stripped == "":
            close_lists()
            i += 1
            continue

        # --- Horizontal rule ---
        if re.match(r'^-{3,}$', stripped) or re.match(r'^\*{3,}$', stripped):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        # --- Headings ---
        m = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if m:
            close_lists()
            level = len(m.group(1))
            heading_raw = normalize_title(m.group(2))
            heading_text = inline(heading_raw)
            heading_id = make_id(heading_raw)
            out.append(f'<h{level} id="{heading_id}">{heading_text}</h{level}>')
            i += 1
            continue

        # --- Blockquote ---
        # Consecutive lines starting with '>' collapse into a single
        # <blockquote>. A blank line or a non-'>' line ends the quote.
        # Supports nested bullet lists (`> - item`) and paragraph breaks.
        if re.match(r'^>\s?', raw.lstrip()):
            close_lists()
            quote_lines = []
            while i < len(lines):
                cur = lines[i]
                bm = re.match(r'^\s*>\s?(.*)$', cur)
                if not bm:
                    break
                quote_lines.append(bm.group(1))
                i += 1

            out.append("<blockquote>")
            para_buf = []  # accumulates text lines for the current <p>
            in_quote_ul = False

            def flush_para():
                nonlocal para_buf
                if para_buf:
                    out.append(f"<p>{inline(' '.join(para_buf))}</p>")
                    para_buf = []

            def close_quote_ul():
                nonlocal in_quote_ul
                if in_quote_ul:
                    out.append("</ul>")
                    in_quote_ul = False

            for ql in quote_lines:
                stripped_ql = ql.strip()
                if stripped_ql == "":
                    # Blank line within blockquote = paragraph break
                    flush_para()
                    close_quote_ul()
                    continue

                # Bullet line inside the quote: `- item`, `* item`, or `◆ item`
                ulm = re.match(r'^[◆\-\*]\s+(.*)', stripped_ql)
                if ulm:
                    flush_para()
                    if not in_quote_ul:
                        out.append("<ul>")
                        in_quote_ul = True
                    out.append(f"<li>{inline(ulm.group(1))}</li>")
                    continue

                # Regular text line: bullets end, accumulate into paragraph
                close_quote_ul()
                para_buf.append(stripped_ql)

            flush_para()
            close_quote_ul()
            out.append("</blockquote>")
            continue

        # --- GFM table ---
        # A table is a line containing pipes whose next line is a
        # separator row like |---|---| (outer pipes optional). Supports
        # both "| a | b |" and compact "a | b" styles.
        if "|" in stripped and not stripped.startswith("|---") and stripped.count("|") >= 1:
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if is_table_separator(nxt):
                close_lists()
                header_cells = split_table_row(stripped)
                sep_cells = split_table_row(nxt)
                # Reject obvious mismatches (prevents runaway captures).
                if len(sep_cells) == len(header_cells) and len(header_cells) >= 2:
                    i += 2  # skip header + separator
                    body_rows = []
                    while i < len(lines):
                        row = lines[i].rstrip()
                        if row.strip() == "":
                            break
                        if "|" not in row:
                            break
                        cells = split_table_row(row.strip())
                        # Stop if the row clearly isn't a table row.
                        if len(cells) == 0:
                            break
                        body_rows.append(cells)
                        i += 1
                    out.append("<table>")
                    out.append("<thead><tr>")
                    for c in header_cells:
                        out.append(f"<th>{inline(c)}</th>")
                    out.append("</tr></thead>")
                    out.append("<tbody>")
                    for row in body_rows:
                        out.append("<tr>")
                        for c in row:
                            out.append(f"<td>{inline(c)}</td>")
                        out.append("</tr>")
                    out.append("</tbody>")
                    out.append("</table>")
                    continue

        # --- Screenshot placeholder ---
        # Accepts: [截圖: xxx], [截圖：xxx], [截圖 xxx], ![截圖](path),
        # and also tolerates surrounding whitespace.
        sm = re.match(r'^!?\[截圖[:：\s]?\s*(.*?)\s*\]\s*(?:\(([^)]*)\))?\s*$', stripped)
        if sm:
            close_lists()
            desc = html.escape(sm.group(1)) if sm.group(1) else ""
            out.append(f'<div class="screenshot-placeholder">[截圖] {desc}</div>')
            i += 1
            continue

        # --- Ordered list ---
        om = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if om:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline(om.group(2))}</li>")
            i += 1
            continue

        # --- Bullet lines (◆ or - or * at start) ---
        bm = re.match(r'^[◆\-\*]\s+(.*)', stripped)
        if bm:
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(bm.group(1))}</li>")
            i += 1
            continue

        # --- Normal paragraph ---
        close_lists()
        out.append(f"<p>{inline(stripped)}</p>")
        i += 1

    close_lists()

    # Safety net: if the parser still thinks it's inside a code block at
    # EOF, forcibly close it and warn to stderr. This protects printed
    # output from runaway <pre><code> blocks caused by unmatched ``` fences
    # in source markdown.
    if in_code:
        sys.stderr.write(
            f"[build-book] WARNING: unclosed code fence in "
            f"{source_name or '<unknown>'}; forcing close.\n"
        )
        out.append("</code></pre>")

    return "\n".join(out)


def split_table_row(row: str):
    """Split a markdown table row into cells, trimming whitespace and
    dropping the leading/trailing empty cells caused by outer pipes."""
    parts = row.split("|")
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def inline(text: str) -> str:
    """Handle inline formatting: bold, inline code, links."""
    t = html.escape(text)
    # inline code (before bold so backticks inside bold don't clash)
    t = re.sub(r'`([^`]+)`', r'<code class="inline">\1</code>', t)
    # bold
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    # links [text](url)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    return t


def normalize_title(text: str) -> str:
    """Normalize punctuation inside chapter/heading titles so output is
    consistent across the book: half-width colon/parens/dashes around the
    chapter title become their full-width counterparts."""
    # Only normalize the first-line title punctuation; leave body content
    # alone. We target the chapter-title shape: "第N講：xxx - yyy" ->
    # "第N講：xxx — yyy".
    t = text
    # Half-width ASCII parens -> full-width (common in chapter titles)
    t = t.replace("(", "（").replace(")", "）")
    # Half-width colon -> full-width colon
    t = t.replace(":", "：")
    # Bare ASCII hyphen used as a chapter-title separator -> em dash
    # (only when surrounded by spaces to avoid catching inline dashes).
    t = re.sub(r'\s-\s', ' — ', t)
    return t


def make_id(text: str) -> str:
    """Create a slug id from heading text."""
    t = re.sub(r'[^\w\u4e00-\u9fff\-]', '-', text)
    return re.sub(r'-+', '-', t).strip('-').lower()


# ---------------------------------------------------------------------------
# Gather files
# ---------------------------------------------------------------------------

def gather_chapters():
    files = sorted(
        f for f in os.listdir(INPUT_DIR)
        if CHAPTER_PATTERN.match(f) and f not in NON_CHAPTER_FILES
    )
    chapters = []
    for idx, fname in enumerate(files, 1):
        path = os.path.join(INPUT_DIR, fname)
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        # Extract title from first # heading
        m = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        raw_title = m.group(1).strip() if m else fname.replace(".md", "")
        title = normalize_title(raw_title)
        chapter_id = f"chapter-{idx}"
        chapters.append({
            "idx": idx,
            "title": title,
            "id": chapter_id,
            "html": md_to_html(content, source_name=fname),
        })
    return chapters


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

CSS = r"""
:root {
  --font-body: 'Songti TC', 'Source Han Serif TC', 'Noto Serif CJK TC', 'Noto Serif TC', 'Times New Roman', serif;
  --font-mono: 'SF Mono', 'Menlo', 'Consolas', 'Courier New', monospace;
  --page-max: 210mm;
  --margin: 2.5cm;
  --color-bg: #fff;
  --color-text: #1a1a1a;
  --color-accent: #8b0000;
  --color-light: #f5f5f0;
  --color-border: #ccc;
}

@page {
  size: A4;
  margin: 25mm 20mm;
}

*, *::before, *::after { box-sizing: border-box; }

html { font-size: 12pt; }

body {
  font-family: var(--font-body);
  color: var(--color-text);
  background: #e8e4df;
  margin: 0;
  padding: 0;
  line-height: 1.75;
  counter-reset: page-counter;
}

.page {
  max-width: var(--page-max);
  margin: 1cm auto;
  padding: var(--margin);
  background: var(--color-bg);
  box-shadow: 0 1px 8px rgba(0,0,0,0.12);
  position: relative;
  min-height: 297mm;
}

.page::after {
  counter-increment: page-counter;
  content: counter(page-counter);
  position: absolute;
  bottom: 1.2cm;
  right: var(--margin);
  font-size: 9pt;
  color: #999;
}

/* ----- Cover ----- */
.cover {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  min-height: 297mm;
}
.cover::after { content: none; }
.cover h1 {
  font-size: 28pt;
  margin: 0 0 0.3em;
  letter-spacing: 0.08em;
  color: var(--color-accent);
}
.cover .subtitle {
  font-size: 16pt;
  color: #555;
  margin-bottom: 2em;
}
.cover .authors {
  font-size: 14pt;
  color: #333;
  margin-bottom: 1em;
}
.cover .year {
  font-size: 11pt;
  color: #999;
}
.cover .ornament {
  width: 60%;
  max-width: 300px;
  border-top: 2px solid var(--color-accent);
  margin: 1.5em auto;
}

/* ----- TOC ----- */
.toc h2 {
  font-size: 20pt;
  color: var(--color-accent);
  margin-bottom: 0.8em;
  text-align: center;
}
.toc ol {
  list-style: none;
  padding: 0;
  margin: 0;
}
.toc li {
  border-bottom: 1px dotted var(--color-border);
  padding: 0.35em 0;
}
.toc li a {
  text-decoration: none;
  color: var(--color-text);
  display: flex;
  justify-content: space-between;
}
.toc li a:hover { color: var(--color-accent); }
.toc li .toc-num {
  font-weight: bold;
  margin-right: 0.6em;
  min-width: 2.5em;
}

/* ----- Chapter ----- */
.chapter { page-break-before: always; break-before: page; }
.chapter h1 {
  font-size: 22pt;
  color: var(--color-accent);
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: 0.3em;
  margin-top: 0;
}
h2 { font-size: 16pt; margin-top: 1.6em; color: #333; }
h3 { font-size: 13pt; margin-top: 1.3em; color: #444; }
h4 { font-size: 12pt; margin-top: 1.1em; font-style: italic; }
h5, h6 { font-size: 11pt; margin-top: 1em; }

p { margin: 0.6em 0; text-align: justify; }

strong { color: #222; }

ul, ol {
  margin: 0.5em 0 0.5em 1.5em;
  padding: 0;
}
ul { list-style: disc; }
ol { list-style: decimal; }
li { margin-bottom: 0.25em; }

hr {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 1.5em 0;
}

a { color: var(--color-accent); }

pre {
  background: var(--color-light);
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.8em 1em;
  overflow-x: auto;
  font-size: 9.5pt;
  line-height: 1.5;
  margin: 0.8em 0;
}
pre code {
  font-family: var(--font-mono);
  background: none;
  padding: 0;
}
code.inline {
  font-family: var(--font-mono);
  background: var(--color-light);
  padding: 0.1em 0.35em;
  border-radius: 3px;
  font-size: 0.9em;
}

/* ----- Tables ----- */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
  font-size: 10.5pt;
}
table th, table td {
  border: 1px solid var(--color-border);
  padding: 0.4em 0.6em;
  text-align: left;
  vertical-align: top;
}
table thead th {
  background: var(--color-light);
  font-weight: bold;
}
table tbody tr:nth-child(even) td {
  background: #fafaf7;
}

/* ----- Blockquote ----- */
blockquote {
  margin: 1.1em 0 1.1em;
  padding: 0.7em 1.1em 0.75em;
  background: #faf7f2;
  border-left: 4px solid #d87a3e;
  color: #555;
  font-style: italic;
  border-radius: 0 4px 4px 0;
}
blockquote p {
  margin: 0.4em 0;
  text-align: left;
}
blockquote p:first-child { margin-top: 0; }
blockquote p:last-child { margin-bottom: 0; }
blockquote ul,
blockquote ol {
  margin: 0.35em 0 0.35em 1.3em;
  padding: 0;
  color: #555;
}
blockquote ul { list-style: disc; }
blockquote ol { list-style: decimal; }
blockquote li {
  margin-bottom: 0.2em;
  text-align: left;
  font-style: italic;
}
/* Tighter spacing when a paragraph is immediately followed by a list */
blockquote p + ul,
blockquote p + ol {
  margin-top: 0.2em;
}
blockquote ul:last-child,
blockquote ol:last-child { margin-bottom: 0; }
blockquote ul:first-child,
blockquote ol:first-child { margin-top: 0; }
/* Ensure a paragraph immediately after a blockquote has breathing room */
blockquote + p { margin-top: 0.9em; }

.screenshot-placeholder {
  background: #eee;
  border: 2px dashed #bbb;
  border-radius: 6px;
  padding: 2em 1.5em;
  text-align: center;
  color: #888;
  font-size: 10pt;
  margin: 1em 0;
}

img { max-width: 100%; height: auto; }

/* ----- Print ----- */
@media print {
  body { background: #fff; }
  .page {
    box-shadow: none;
    margin: 0;
    padding: var(--margin);
    min-height: auto;
    page-break-after: always;
  }
  .page::after {
    position: fixed;
    bottom: 1cm;
    right: 1.5cm;
  }
  .cover { page-break-after: always; }
  .chapter { page-break-before: always; }
  h1, h2, h3, h4 {
    page-break-after: avoid;
    break-after: avoid;
  }
  h1, h2, h3, h4, li, pre, table, .screenshot-placeholder {
    page-break-inside: avoid;
    break-inside: avoid;
  }
  img { max-width: 100%; }
  pre { white-space: pre-wrap; word-wrap: break-word; }
}
"""


def build_html(chapters):
    toc_items = []
    for ch in chapters:
        num = f"{ch['idx']:02d}"
        toc_items.append(
            f'<li><a href="#{ch["id"]}"><span class="toc-num">{num}</span>'
            f'<span>{html.escape(ch["title"])}</span></a></li>'
        )

    chapter_blocks = []
    for ch in chapters:
        chapter_blocks.append(
            f'<div class="page chapter" id="{ch["id"]}">\n{ch["html"]}\n</div>'
        )

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{BOOK_TITLE} — {BOOK_SUBTITLE}</title>
<style>
{CSS}
</style>
</head>
<body>

<!-- Cover -->
<div class="page cover">
  <h1>{BOOK_TITLE}</h1>
  <div class="ornament"></div>
  <div class="subtitle">{BOOK_SUBTITLE}</div>
  <div class="authors">作者：{BOOK_AUTHORS}</div>
  <div class="year">2026</div>
</div>

<!-- Table of Contents -->
<div class="page toc">
  <h2>目 錄</h2>
  <ol>
    {''.join(toc_items)}
  </ol>
</div>

<!-- Chapters -->
{''.join(chapter_blocks)}

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Reading lectures from: {INPUT_DIR}")
    chapters = gather_chapters()
    print(f"  Found {len(chapters)} chapters")

    content = build_html(chapters)
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(content)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"  Written: {OUTPUT_FILE}")
    print(f"  Size: {size_kb:.1f} KB")

    # Open in browser
    if sys.platform == "darwin":
        subprocess.Popen(["open", OUTPUT_FILE])
    elif sys.platform == "linux":
        subprocess.Popen(["xdg-open", OUTPUT_FILE])
    print("  Opened in browser.")


if __name__ == "__main__":
    main()
