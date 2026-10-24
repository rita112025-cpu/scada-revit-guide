"""Render the teaching Markdown to paginated PDFs with the installed PyMuPDF."""

from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote

import pymupdf


OUT = Path(__file__).resolve().parents[1]
CSS = """body { font-family: sans-serif; font-size: 10.5pt; line-height: 1.5; color: #172c3b; }
h1 { font-size: 23pt; color: #18364e; margin-bottom: 18pt; }
h2 { font-size: 16pt; color: #18364e; margin-top: 20pt; page-break-after: avoid; }
h3 { font-size: 13pt; color: #234f70; margin-top: 14pt; page-break-after: avoid; }
p { margin-top: 0; margin-bottom: 7pt; }
.source { font-size: 8pt; color: #546574; }
.step { margin-left: 8pt; }
table { width: 100%; border-collapse: collapse; margin-top: 7pt; margin-bottom: 12pt; font-size: 9pt; }
td, th { border: 0.5pt solid #cbd5de; padding: 5pt; vertical-align: top; }
th { background-color: #e7eef5; color: #18364e; }
a { color: #146c94; text-decoration: none; }
"""


def inline(text: str, source: Path) -> str:
    """Escape body text while preserving explicit local and web hyperlinks."""
    chunks, last = [], 0
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        chunks.append(html.escape(text[last:match.start()].replace("`", "")))
        label, target = match.groups()
        if target.startswith(("http://", "https://")):
            chunks.append(f'<a href="{html.escape(target, quote=True)}">{html.escape(label)}</a>')
        else:
            # Portable print copies retain source names; Word/CSV provide file links.
            chunks.append(html.escape(label))
        last = match.end()
    chunks.append(html.escape(text[last:].replace("`", "")))
    return "".join(chunks)


def to_html(source: Path) -> str:
    """Convert the deliberately limited teaching Markdown into print markup."""
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    parts, anchor, i = ["<html><body>"], None, 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("<!--"):
            continue
        match = re.fullmatch(r'<a id="([^"]+)"></a>', line)
        if match:
            anchor = match[1]
            continue
        if line.startswith("|"):
            rows = [line]
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            parsed_rows = []
            for row in rows:
                cells = [cell.strip() for cell in row.strip("|").split("|")]
                if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                    continue
                parsed_rows.append(cells)
            if source.name.startswith("03_"):
                # A stacked layout keeps lengthy bilingual evidence readable on A4.
                for row in parsed_rows[1:]:
                    fields = [f"<b>{inline(label, source)}：</b>{inline(value, source)}" for label, value in zip(parsed_rows[0], row)]
                    parts.append('<p style="margin-bottom:10pt">' + "<br>".join(fields) + "</p>")
            else:
                # Repeat table headings and bound the size of each pagination unit.
                for start in range(1, len(parsed_rows), 12):
                    parts.append("<table>")
                    for number, cells in enumerate([parsed_rows[0], *parsed_rows[start:start + 12]]):
                        tag = "th" if number == 0 else "td"
                        parts.append("<tr>" + "".join(f"<{tag}>{inline(cell, source)}</{tag}>" for cell in cells) + "</tr>")
                    parts.append("</table>")
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            level = len(heading[1])
            attrib = f' id="{anchor}"' if anchor else ""
            parts.append(f"<h{level}{attrib}>{inline(heading[2], source)}</h{level}>")
            anchor = None
        else:
            cls = "source" if line.startswith("來源影片：") else "step" if re.match(r"^(?:\d+\.|-) ", line) else "body"
            parts.append(f'<p class="{cls}">{inline(line, source)}</p>')
    parts.append("</body></html>")
    return "\n".join(parts)


def layout(rect_number: int, filled: pymupdf.Rect) -> tuple[pymupdf.Rect, pymupdf.Rect, None]:
    """Provide a consistent A4 content area on every page."""
    del filled
    if rect_number > 100:
        raise ValueError("Document pagination exceeded 100 A4 pages; inspect oversized content.")
    media = pymupdf.paper_rect("a4")
    return media, pymupdf.Rect(43, 45, media.width - 43, media.height - 45), None


def normalized(text: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text)).replace("`", "")


def verify_text(source: Path, text: str) -> None:
    """Require every source paragraph and table cell to survive PDF pagination."""
    actual = normalized(text)
    for line in source.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.startswith(("<!--", "<a ")):
            continue
        line = re.sub(r"^#{1,4}\s+", "", line).strip()
        cells = [cell.strip() for cell in line.strip("|").split("|")] if line.startswith("|") else [line.removeprefix("- ")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        for cell in cells:
            cell = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cell)
            if normalized(cell) and normalized(cell) not in actual:
                raise ValueError(f"PDF text omitted: {source.name}: {cell[:80]}")


def print_sections(markup: str, source: Path) -> list[str]:
    """Give each short MEP lesson its own print page and retain chapter context."""
    if not source.name.startswith("01_"):
        return [markup]
    sections, pending = [], ""
    for segment in re.split(r"(?=<h[23]\b)", markup):
        if not segment.strip():
            continue
        if re.match(r"<h2>第 \d+ 章", segment):
            pending += segment
        elif re.match(r'<h3\b[^>]*>M\d{2}', segment):
            sections.append(pending + segment)
            pending = ""
        elif segment.startswith("<h2>本冊整合成果") and sections:
            sections[-1] += segment
        else:
            sections.append(segment)
    if pending:
        sections.append(pending)
    return sections


def main() -> None:
    report = []
    for source in sorted(OUT.glob("0[0-4]_*.md")):
        markup = to_html(source).removeprefix("<html><body>\n").removesuffix("\n</body></html>")
        document = pymupdf.open()
        toc = []
        for section in print_sections(markup, source):
            if not section.strip():
                continue
            story = pymupdf.Story("<html><body>" + section + "</body></html>", user_css=CSS)
            part = story.write_with_links(layout)
            heading = re.search(r"<h[123][^>]*>(.*?)</h[123]>", section)
            if heading:
                title = html.unescape(re.sub(r"<[^>]+>", "", heading[1]))
                toc.append([1, title, len(document) + 1])
            document.insert_pdf(part)
            part.close()
        text = "\n".join(page.get_text() for page in document)
        verify_text(source, text)
        if len(normalized(text)) < 500 or "\ufffd" in text:
            raise ValueError(f"PDF has missing text: {source.name}")
        for unit in re.findall(r'^<a id="([mr]\d{2})"></a>$', source.read_text(encoding="utf-8-sig"), re.M):
            if unit.upper() not in text:
                raise ValueError(f"PDF is missing unit {unit}: {source.name}")
        for number, page in enumerate(document):
            page.insert_text((43, page.rect.height - 23), f"Revit 2025 | 2026-10-24 | {number + 1}/{len(document)}", fontsize=8, color=(0.3, 0.38, 0.44))
        target = source.with_suffix(".pdf")
        document.set_toc(toc)
        document.set_metadata({"title": source.stem, "author": "Revit course teaching materials", "subject": "Revit 2025 Traditional Chinese"})
        document.save(target, garbage=4, deflate=True)
        report.append({"file": target.name, "pages": len(document), "extracted_characters": len(text), "links": sum(len(page.get_links()) for page in document), "all_paragraphs_and_cells_verified": True})
        document.close()
        print(json.dumps(report[-1], ensure_ascii=False), flush=True)
    (OUT / "工具" / "PDF檢核結果.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
