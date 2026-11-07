#!/usr/bin/env python3
"""Regenerate in-site HTML for 給排水與視圖教材 and splice into index.html.

Source of truth for teaching prose remains the Markdown files under
給排水與視圖教材/. This script only rebuilds the embedded reading chrome
inside index.html (Rank 5).

Usage (from repo root):
  python3 scripts/embed_plumbing.py
"""
from __future__ import annotations

import html as html_lib
import pathlib
import re
import sys

try:
    import markdown
except ImportError:
    sys.stderr.write("Install markdown: pip install markdown\n")
    sys.exit(1)

ROOT = pathlib.Path(__file__).resolve().parents[1]
MD_DIR = ROOT / "給排水與視圖教材"
INDEX = ROOT / "index.html"

CHAPTERS = [
    {
        "file": "00_閱讀指南.md",
        "id": "plumbing-00",
        "eyebrow": "00",
        "title": "閱讀指南",
        "keywords": "閱讀指南 給排水 視圖教材 練習前準備 學習節奏 Revit 2025",
    },
    {
        "file": "01_給排水建模操作教材.md",
        "id": "plumbing-01",
        "eyebrow": "01",
        "title": "給排水建模操作教材",
        "keywords": "給排水建模 M01 M46 立管 衛工 配管 SP WP VP CW HW 單元目錄",
    },
    {
        "file": "02_族群電氣與視圖管理教材.md",
        "id": "plumbing-02",
        "eyebrow": "02",
        "title": "族群電氣與視圖管理教材",
        "keywords": "族群 電氣 視圖管理 R01 R11 參數化 電纜架 整合課",
    },
    {
        "file": "03_術語與操作校正表.md",
        "id": "plumbing-03",
        "eyebrow": "03",
        "title": "術語與操作校正表",
        "keywords": "術語 校正表 功能名稱 待確認 官方依據",
    },
    {
        "file": "04_練習與驗收.md",
        "id": "plumbing-04",
        "eyebrow": "04",
        "title": "練習與驗收",
        "keywords": "練習 驗收 作業 檢查點 學習紀錄",
    },
    {
        "file": "07_電氣迴路與配電教材.md",
        "id": "plumbing-07",
        "eyebrow": "07",
        "title": "電氣迴路與配電教材",
        "keywords": "電氣迴路 配電 E01 E09 電壓 負載表 盤體",
    },
]

BOOK_STEMS = {
    "00_閱讀指南": "#plumbing-00",
    "01_給排水建模操作教材": "#plumbing-01",
    "02_族群電氣與視圖管理教材": "#plumbing-02",
    "03_術語與操作校正表": "#plumbing-03",
    "04_練習與驗收": "#plumbing-04",
    "07_電氣迴路與配電教材": "#plumbing-07",
}

TOC_BLOCK = """    <li class="toc-acc">
      <details>
        <summary class="toc-group">給排水與視圖教材</summary>
        <ol class="toc-panel">
          <li><a href="#plumbing-guide" data-keywords="給排水 視圖教材 衛工 配管 族群 電纜架 整合課 閱讀指南 練習 驗收 術語 章節目錄">給排水教材總覽</a></li>
          <li><a href="#plumbing-00" data-keywords="閱讀指南 練習前準備 學習節奏 Revit 2025 版本差異">00 閱讀指南</a></li>
          <li><a href="#plumbing-01" data-keywords="給排水建模 M01 M46 立管 衛工 配管 SP WP VP CW HW 單元目錄">01 給排水建模</a></li>
          <li><a href="#plumbing-02" data-keywords="族群 電氣 視圖管理 R01 R11 參數化 電纜架 整合課">02 族群電氣與視圖</a></li>
          <li><a href="#plumbing-03" data-keywords="術語 校正表 功能名稱 待確認 官方依據">03 術語校正表</a></li>
          <li><a href="#plumbing-04" data-keywords="練習 驗收 作業 檢查點 學習紀錄">04 練習與驗收</a></li>
          <li><a href="#plumbing-07" data-keywords="電氣迴路 配電 E01 E09 電壓 負載表 盤體">07 電氣迴路與配電</a></li>
        </ol>
      </details>
    </li>"""

HUB = """<section id="plumbing-guide" class="section">
<h2><span class="eyebrow">給排水與視圖</span>給排水與視圖教材（Revit 2025）</h2>
<p>給排水建模、族群與電氣、視圖管理的操作教材。章節已嵌在本站同一套閱讀介面（側欄、徽章、字級、暗版）；請先讀閱讀指南的順序，再依 01→04 練習，需要完整電氣迴路時再讀 07。</p>
<p class="paths-intro">章節目錄</p>
<div class="paths" role="navigation" aria-label="給排水教材章節">
  <a class="path-card" href="#plumbing-00"><div class="k">00</div><h3>閱讀指南</h3><p>閱讀順序、版本差異、練習前準備與學習節奏。</p><span class="go">開始閱讀 →</span></a>
  <a class="path-card" href="#plumbing-01"><div class="k">01</div><h3>給排水建模操作教材</h3><p>M01–M46：基準、器具、排水、標註、給水與協調。含單元目錄表。</p><span class="go">進入建模 →</span></a>
  <a class="path-card" href="#plumbing-02"><div class="k">02</div><h3>族群電氣與視圖管理</h3><p>R01–R11：參數化族群、盤體、視圖樣板與整合課。</p><span class="go">進入專題 →</span></a>
  <a class="path-card" href="#plumbing-03"><div class="k">03</div><h3>術語與操作校正表</h3><p>用語對照、功能名稱、概念修正與待確認事項。</p><span class="go">查校正表 →</span></a>
  <a class="path-card" href="#plumbing-04"><div class="k">04</div><h3>練習與驗收</h3><p>可實作作業、檢查點、參考答案與學習紀錄。</p><span class="go">去做練習 →</span></a>
  <a class="path-card" href="#plumbing-07"><div class="k">07</div><h3>電氣迴路與配電</h3><p>E01–E09：電壓、配電系統、迴路、路徑與負載表。</p><span class="go">進入迴路 →</span></a>
</div>
<p class="note">影片對照索引（CSV）：<a href="給排水與視圖教材/05_影片對照索引.csv">05_影片對照索引.csv</a>。各章仍保留 Markdown 原文連結，供對照或離線閱讀。</p>
</section>
"""

CSS_EXTRA = """
/* Rank 5: in-site 給排水教材 */
.unit-nav{
  margin:12px 0 22px; padding:14px 16px;
  background:var(--accent-soft); border:1px solid var(--border);
  border-radius:var(--radius-sm);
}
.unit-nav .table-scroll{margin:8px 0 0}
.unit-nav table.compare th:first-child,
.unit-nav table.compare td:first-child{white-space:nowrap; width:4.5em}
.section h4{font-size:18px; font-weight:800; margin:22px 0 8px; scroll-margin-top:88px}
.section h5{font-size:16px; font-weight:800; margin:16px 0 6px; scroll-margin-top:88px}
.plumbing-chapter .step-body > h3{scroll-margin-top:88px}
.plumbing-chapter .step-body > p:first-of-type{color:var(--text-muted)}
"""


def slugify_zh(text: str) -> str:
    t = re.sub(r"\s+", "-", text.strip())
    t = re.sub(r"[^\w\u4e00-\u9fff\-]+", "", t, flags=re.UNICODE)
    return t[:48] or "sec"


def preprocess_md(src: str) -> str:
    def attach_id(m):
        aid = m.group(1)
        hashes = m.group(2)
        title = m.group(3)
        return f"{hashes} {title} {{#{aid}}}"

    return re.sub(
        r'<a\s+id="([a-zA-Z0-9_-]+)"\s*></a>\s*\n+(#{2,6})\s+(.+)',
        attach_id,
        src,
    )


def rewrite_cross_refs(html: str) -> str:
    def book_repl(m):
        inner = m.group(1)
        for key, href in BOOK_STEMS.items():
            if key in inner or inner.replace(" ", "_") == key:
                return f'<a href="{href}">《{inner}》</a>'
        if "05_影片對照索引" in inner:
            return (
                f'<a href="給排水與視圖教材/05_影片對照索引.csv">《{inner}》</a>'
            )
        return m.group(0)

    html = re.sub(r"《([^》]+)》", book_repl, html)

    def md_href(m):
        stem = m.group(1)
        if stem in BOOK_STEMS:
            return f'href="{BOOK_STEMS[stem]}"'
        return m.group(0)

    html = re.sub(
        r'href="(?:\./)?(?:給排水與視圖教材/)?(0[0-47]_[^"]+?)\.md"',
        md_href,
        html,
    )
    return html


def postprocess_body(html: str, chapter_id: str) -> str:
    html = re.sub(r"^<h1>[^<]*</h1>\s*", "", html)

    html = html.replace("<h4", "<hX4").replace("</h4>", "</hX4>")
    html = html.replace("<h3", "<hX3").replace("</h3>", "</hX3>")
    html = html.replace("<h2", "<h3").replace("</h2>", "</h3>")
    html = html.replace("<hX3", "<h4").replace("</hX3>", "</h4>")
    html = html.replace("<hX4", "<h5").replace("</hX4>", "</h5>")

    def add_h3_id(m):
        attrs = m.group(1) or ""
        inner = m.group(2)
        if re.search(r"\bid=", attrs):
            return m.group(0)
        text = re.sub(r"<[^>]+>", "", inner)
        sid = slugify_zh(text)
        if not re.match(r"^(m|r|e)\d{2}$", sid, re.I):
            sid = f"{chapter_id}-{sid}"
        return f'<h3 id="{sid}"{attrs}>{inner}</h3>'

    html = re.sub(r"<h3([^>]*)>(.*?)</h3>", add_h3_id, html, flags=re.S)

    def wrap_table(m):
        table = m.group(0)
        if "class=" not in table:
            table = table.replace("<table>", '<table class="compare">', 1)
        return f'<div class="table-scroll">{table}</div>'

    html = re.sub(r"<table>.*?</table>", wrap_table, html, flags=re.S)

    html = re.sub(
        r'(<h3[^>]*>單元目錄</h3>\s*)(<div class="table-scroll">)',
        r'\1<div class="unit-nav">\2',
        html,
        count=1,
    )
    if '<div class="unit-nav">' in html:
        html = re.sub(
            r'(<div class="unit-nav"><div class="table-scroll">.*?</div>)',
            r"\1</div>",
            html,
            count=1,
            flags=re.S,
        )

    return rewrite_cross_refs(html)


def convert_chapter(ch: dict) -> str:
    raw = preprocess_md((MD_DIR / ch["file"]).read_text(encoding="utf-8"))
    body = markdown.markdown(
        raw,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list", "nl2br"],
    )
    body = postprocess_body(body, ch["id"])
    md_href = f"給排水與視圖教材/{ch['file']}"
    return "\n".join(
        [
            f'<section id="{ch["id"]}" class="section plumbing-chapter">',
            f'<h2><span class="eyebrow">給排水教材 · {ch["eyebrow"]}</span>'
            f'{html_lib.escape(ch["title"])}</h2>',
            '<div class="step-body">',
            body,
            "</div>",
            f'<p class="note">本章 Markdown 原文：'
            f'<a href="{md_href}">{html_lib.escape(ch["file"])}</a>'
            f"（本站已嵌成網頁，不必離開側欄閱讀）。</p>",
            "</section>",
            "",
        ]
    )


def build_fragment() -> str:
    return "\n".join([HUB] + [convert_chapter(ch) for ch in CHAPTERS]).rstrip() + "\n"


def splice_index(html: str, fragment: str) -> str:
    if "/* Rank 5: in-site" not in html:
        html = html.replace("</style>", CSS_EXTRA + "</style>", 1)

    html = re.sub(
        r'    <li class="toc-acc">\s*'
        r"<details>\s*"
        r'<summary class="toc-group">給排水與視圖教材</summary>\s*'
        r'<ol class="toc-panel">[\s\S]*?</ol>\s*'
        r"</details>\s*"
        r"</li>",
        TOC_BLOCK,
        html,
        count=1,
    )

    html = re.sub(
        r'<section id="plumbing-guide" class="section">[\s\S]*?</section>'
        r'(?:\s*<section id="plumbing-\d{2}" class="section plumbing-chapter">'
        r"[\s\S]*?</section>)*",
        fragment.rstrip(),
        html,
        count=1,
    )

    html = re.sub(
        r"const MEGA_LESSONS = \[[^\]]*\];",
        "const MEGA_LESSONS = ['mep-intro','cam-intro','side-drop',"
        "'batch-vt','viewer-blank','plot-trouble',"
        "'plumbing-01','plumbing-02','plumbing-07'];",
        html,
        count=1,
    )

    html = html.replace(
        "<p>給排水建模、族群與視圖管理。從閱讀指南進入 00–04；側欄另有視圖樣板與雲端排查。</p>\n"
        '    <span class="go">查看給排水教材 →</span>',
        "<p>給排水建模、族群與視圖管理。章節已嵌在本站；從閱讀指南進入 00–04／07。</p>\n"
        '    <span class="go">進入給排水教材 →</span>',
        1,
    )
    html = html.replace(
        "<p>給排水建模、族群與視圖管理。章節已嵌在本站；從閱讀指南進入 00–04／07。</p>\n"
        '    <span class="go">進入給排水教材 →</span>',
        "<p>給排水建模、族群與視圖管理。章節已嵌在本站；從閱讀指南進入 00–04／07。</p>\n"
        '    <span class="go">進入給排水教材 →</span>',
        1,
    )
    return html


def main() -> None:
    fragment = build_fragment()
    html = INDEX.read_text(encoding="utf-8")
    updated = splice_index(html, fragment)
    INDEX.write_text(updated, encoding="utf-8")
    print(f"Updated {INDEX} ({INDEX.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
