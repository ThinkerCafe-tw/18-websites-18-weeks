#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
visual-check.py — 18-websites-18-weeks 視覺 CI 檢查
靜態掃描 websites/*.html，抓出以下風險：
  1) 圖片 URL 是否可達（404/500 = RED；<1KB = YELLOW）
  2) Unsplash 人像圖是否設 &crop=faces
  3) Hero 區塊：深色背景 + 無明確文字顏色 = YELLOW
  4) Sticky footer pattern 是否存在 = YELLOW
輸出 [RED]/[YELLOW] 清單；RED > 0 則 exit 1。
"""
import os
import re
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    print("ERROR: 需要 requests 套件，請先 pip install requests", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).parent.resolve()
WEBSITES_DIR = REPO_ROOT / "websites"

# ---------- 規則表 ----------
PORTRAIT_KEYWORDS = [
    "headshot", "portrait", "people", "team", "person",
    "face", "man", "woman", "lawyer", "coach", "trainer",
    "therapist", "counselor", "doctor",
]
DARK_COLOR_TOKENS = [
    "#000", "#111", "#222", "#333", "#0a", "#1a", "#2a",
    "rgb(0,0,0)", "rgba(0,0,0", "black", "navy", "midnight",
    "dark", "#10", "#20", "#30", "linear-gradient",
]

# ---------- 結果容器 ----------
RED = []
YELLOW = []


def add_red(file_rel, msg):
    RED.append((file_rel, msg))


def add_yellow(file_rel, msg):
    YELLOW.append((file_rel, msg))


# ---------- 1) 圖片 URL 檢查 ----------
IMG_SRC_RE = re.compile(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', re.IGNORECASE)
CSS_URL_RE = re.compile(r'url\(["\']?(https?://[^)"\']+)["\']?\)', re.IGNORECASE)


def collect_image_urls(html, file_rel):
    urls = set()
    for m in IMG_SRC_RE.finditer(html):
        urls.add(m.group(1))
    for m in CSS_URL_RE.finditer(html):
        urls.add(m.group(1))
    return [(file_rel, u) for u in urls]


def probe_url(item):
    file_rel, url = item
    try:
        # 先用 HEAD，失敗時 fallback GET（Unsplash 有時 HEAD 行為不一致）
        r = requests.head(url, allow_redirects=True, timeout=8)
        if r.status_code >= 400:
            r = requests.get(url, stream=True, allow_redirects=True, timeout=10)
        status = r.status_code
        size = None
        cl = r.headers.get("content-length")
        if cl and cl.isdigit():
            size = int(cl)
        return (file_rel, url, status, size, None)
    except requests.RequestException as e:
        return (file_rel, url, 0, None, str(e)[:120])


def check_images(files):
    all_items = []
    for fp, html in files:
        all_items.extend(collect_image_urls(html, fp))
    total = len(all_items)
    failed = 0
    suspicious = 0
    if not all_items:
        return total, failed, suspicious

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(probe_url, it) for it in all_items]
        for fut in as_completed(futures):
            file_rel, url, status, size, err = fut.result()
            if err:
                add_red(file_rel, f"image URL unreachable ({err}) - {url}")
                failed += 1
                continue
            if status in (404, 410):
                add_red(file_rel, f"image URL {status} - {url}")
                failed += 1
            elif status >= 500:
                add_red(file_rel, f"image URL {status} - {url}")
                failed += 1
            elif status >= 400:
                add_red(file_rel, f"image URL {status} - {url}")
                failed += 1
            elif size is not None and size < 1024:
                add_yellow(file_rel, f"image <1KB ({size}B) may be error page - {url}")
                suspicious += 1
    return total, failed, suspicious


# ---------- 2) 人臉 crop 檢查 ----------
UNSPLASH_RE = re.compile(
    r'https?://(?:images|source)\.unsplash\.com/[^\s"\'<>)]+',
    re.IGNORECASE,
)


def check_face_crop(files):
    total = 0
    missing = 0
    for file_rel, html in files:
        for m in UNSPLASH_RE.finditer(html):
            url = m.group(0)
            lower = url.lower()
            is_portrait = any(kw in lower for kw in PORTRAIT_KEYWORDS)
            if not is_portrait:
                continue
            total += 1
            if "crop=faces" not in lower and "crop=face" not in lower:
                add_yellow(
                    file_rel,
                    f"portrait image missing crop=faces - {url}",
                )
                missing += 1
    return total, missing


# ---------- 3) Hero 文字顏色檢查 ----------
HERO_CLASS_RE = re.compile(
    r'(?:class=["\'][^"\']*\bhero(?:-section)?\b[^"\']*["\']'
    r'|data-block=["\']hero["\'])',
    re.IGNORECASE,
)
# 粗略抓 CSS 規則塊：.hero-section { ... } 或 [data-block="hero"] { ... }
HERO_CSS_BLOCK_RE = re.compile(
    r'(\.hero(?:-section)?|\[data-block=["\']hero["\']\])([^{]*)\{([^}]*)\}',
    re.IGNORECASE | re.DOTALL,
)


def looks_dark(value):
    v = value.lower()
    return any(tok in v for tok in DARK_COLOR_TOKENS)


def check_hero_colors(files):
    total = 0
    risky = 0
    for file_rel, html in files:
        has_hero = bool(HERO_CLASS_RE.search(html))
        if not has_hero:
            continue
        total += 1
        # 收集所有與 hero 相關的 CSS 規則塊
        hero_blocks = []
        for m in HERO_CSS_BLOCK_RE.finditer(html):
            hero_blocks.append((m.group(1), m.group(3)))
        if not hero_blocks:
            add_yellow(
                file_rel,
                "hero section found but no CSS rule matched (.hero/.hero-section/[data-block=hero])",
            )
            risky += 1
            continue
        # 合併分析：是否有 background + text color
        combined_bg = ""
        combined_color = ""
        for sel, body in hero_blocks:
            bl = body.lower()
            if "background" in bl:
                combined_bg += " " + bl
            if re.search(r"(^|[;\s])color\s*:", bl):
                combined_color += " " + bl
        if combined_bg and looks_dark(combined_bg):
            if not combined_color:
                add_yellow(
                    file_rel,
                    "hero has dark background but no explicit text color → contrast risk",
                )
                risky += 1
    return total, risky


# ---------- 4) Sticky footer 檢查 ----------
# Extract <style> content first, then find body CSS rules within it
# Match body/html,body selectors with their CSS content
# (?:^|[,\s]) ensures body selector starts at line or after comma/whitespace (not after . or -)
BODY_RULE_RE = re.compile(
    r'(?:^|[,\s])(?:html\s*,\s*)?body\b\s*\{([^}]*)\}|(?:^|[,\s])body\s*,\s*html\s*\{([^}]*)\}',
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)


def check_sticky_footer(files):
    total = 0
    missing = 0
    for file_rel, html in files:
        total += 1
        # Extract style content only to avoid matching JS/HTML
        style_match = re.search(r'<style[^>]*>(.*?)</style>', html, re.IGNORECASE | re.DOTALL)
        if not style_match:
            add_yellow(
                file_rel,
                "no <style> tag found",
            )
            missing += 1
            continue
        style_content = style_match.group(1)
        matches = BODY_RULE_RE.findall(style_content)
        if not matches:
            add_yellow(
                file_rel,
                "no body{} CSS rule found → sticky footer pattern unclear",
            )
            missing += 1
            continue
        # 合併所有 body 相關的 CSS 規則內容（每個 match 是 tuple，取非空的那個）
        combined = " ".join(
            (m[0] if m[0] else m[1]).lower()
            for m in matches
        )
        # 檢查 min-height: 100vh (支持有無空格)
        has_min_height = "min-height:100vh" in combined.replace(" ", "") or \
            "min-height: 100vh" in combined
        # 檢查 display: flex 和 flex-direction: column (支持有無空格)
        has_flex_col = ("display:flex" in combined.replace(" ", "") or
                        "display: flex" in combined) and \
            ("flex-direction:column" in combined.replace(" ", "") or
             "flex-direction: column" in combined)
        if not (has_min_height and has_flex_col):
            add_yellow(
                file_rel,
                "body missing sticky-footer pattern (min-height:100vh + flex column)",
            )
            missing += 1
    return total, missing


# ---------- main ----------
def main():
    if not WEBSITES_DIR.exists():
        print(f"ERROR: {WEBSITES_DIR} 不存在", file=sys.stderr)
        return 2
    html_files = sorted(WEBSITES_DIR.glob("*.html"))
    if not html_files:
        print("WARN: 沒有找到任何 websites/*.html")
        return 0

    files = []
    for fp in html_files:
        rel = str(fp.relative_to(REPO_ROOT))
        try:
            html = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            add_red(rel, f"failed to read file: {e}")
            continue
        files.append((rel, html))

    # 可透過環境變數跳過網路請求（CI/pre-commit 慢時用）
    skip_net = os.environ.get("VISUAL_CHECK_SKIP_NET") == "1"
    if skip_net:
        img_total = sum(len(collect_image_urls(h, f)) for f, h in files)
        img_failed = 0
        img_suspect = 0
        print("(VISUAL_CHECK_SKIP_NET=1 → 跳過圖片 URL 網路探測)")
    else:
        img_total, img_failed, img_suspect = check_images(files)

    face_total, face_missing = check_face_crop(files)
    hero_total, hero_risky = check_hero_colors(files)
    footer_total, footer_missing = check_sticky_footer(files)

    print("=== 視覺檢查報告 ===")
    print(f"掃描檔案數：{len(files)}")
    print(f"圖片 URL 檢查：{img_total} 個，{img_failed} 失效")
    print(f"人臉 crop 檢查：{face_total} 個人像 URL，{face_missing} 未設 crop=faces")
    print(f"Hero 文字顏色：{hero_total} 個 hero，{hero_risky} 有風險")
    print(f"Sticky footer：{footer_total} 個檔案，{footer_missing} 有問題")
    print()

    for file_rel, msg in RED:
        print(f"[RED] {file_rel}: {msg}")
    for file_rel, msg in YELLOW:
        print(f"[YELLOW] {file_rel}: {msg}")

    print()
    print(f"RED={len(RED)} YELLOW={len(YELLOW)}")
    return 1 if len(RED) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
