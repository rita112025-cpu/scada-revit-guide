"""Build source indexes and styled DOCX editions using only the standard library."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from urllib.parse import quote, unquote
from xml.etree import ElementTree as ET


OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parent
MEP = ROOT / "MEP影片0317" / "字幕版"
REVIT = ROOT / "Revit課程資料" / "課程影片" / "字幕燒錄版"
BOOKS = {
    "M": OUT / "01_給排水建模操作教材.md",
    "R": OUT / "02_族群電氣與視圖管理教材.md",
}
R_ORDER = [
    "元件基本概念", "00.元件製作(閥件)_1", "00.元件製作(閥件)_2",
    "00.元件製作(閥件)_3", "盤體建置20260731", "07.新增篩選條件",
    "08.視圖樣板", "10.動力系統模型上材質方式", "廠商上午20260730",
    "廠商下午20260730", "廠商上午20260731",
]

# These patterns locate evidence only. No source subtitle or transcript is changed.
RULES = [
    ("T01", "複製間視", "複製／監視", "用語整理", "S01"),
    ("T02", "部線編號|路線編號|布線片號|部線片號|部線偏號|佈線偏號|固陷偏好|步行\n偏好", "佈線偏好 Routing Preferences", "用語整理", "S03"),
    ("T03", "未攻裝置|未工裝置|位工裝置|未攻|未工", "衛工裝置 Plumbing Fixtures", "用語整理", "M05–M07"),
    ("T04", "夜簽|夜千|夜遷|頁纖|頁前|葉籤|業線", "頁籤；依語境判讀", "用語整理", "功能區"),
    ("T05", "性子|性質欄|新展", "性質選項板；需依語境判讀", "用語整理", "S16"),
    ("T06", "仕圖|試圖", "視圖 View", "用語整理", "S16"),
    ("T07", "幾出|舉出", "擠出 Extrusion", "用語整理", "S09"),
    ("T08", "工智|工資", "公制 Metric；樣板完整名稱依本機確認", "用語整理", "R01、R02"),
    ("T09", "倉考|參考領域|參考頻率", "參考平面；依語境判讀", "用語整理", "R01"),
    ("T10", "純水彎|純嘴彎|純水丸|純嘴|沉水管", "存水彎 Trap；依器具與 RFA 確認", "用語整理", "M19–M23"),
    ("T11", "斜梯|協梯|協聽|斜踢", "斜三通／斜向分支配件；以 RFA 為準", "案例限定", "M17、M18、S03"),
    ("T12", "順水梯|順踢|順水踢|順踢", "順水三通；以 RFA 為準", "案例限定", "M15、M16"),
    ("T13", "脊髓管|集水管", "課程所稱的 P 形配件，精確名稱待確認", "待確認", "P03"),
    ("T14", "水雙彎", "器具末端專用接頭，產品名稱待確認", "待確認", "P06"),
    ("T15", "光明式|光明式的", "關聯族群參數 Associate Family Parameters", "用語整理", "S23"),
    ("T16", "物件形式", "物件型式 Object Styles", "用語整理", "S21"),
    ("T17", "Namey|Namei|Namey所有|Namey所", "Navisworks", "用語整理", "R08"),
    ("T18", "脆|吹|Payboard|Pay board", "電纜架 Cable Tray；必須依上下文判讀", "用語整理", "S20"),
    ("T19", "波度|活力", "斜度／坡度；依管放置語境", "用語整理", "S02"),
    ("T20", "力管|立廣|立廣", "立管", "用語整理", "M10–M14"),
    ("T21", "切土", "切割幾何圖形 Cut Geometry", "用語整理", "R01"),
    ("T22", "引數", "參數；屬用語統一，並非一律錯字", "用語整理", "S06"),
    ("T23", "進射", "鏡射 Mirror；依對稱操作語境", "用語整理", "R04"),
    ("T24", "圍爐|迴爐", "迴路 Circuit", "用語整理", "S11"),
    ("T25", "服務型別", "服務類型 Service Type", "用語整理", "R08"),
    ("T26", "高層", "高程或高度；樓層語境另判", "用語整理", "S05"),
    ("C05", "粗糙度", "視圖詳細等級與管材料粗糙度分開", "功能核對", "C05、S16"),
    ("C08", "透明|蓋管|蓋掉", "透明／不透明背景分別判讀", "功能核對", "C08、S05"),
    ("C15", "動力根本就沒有系統|動力的部分沒有系統", "電管路徑分類與電氣迴路分開", "功能核對", "C15、S11"),
    ("C19", "查訊表|size to R|大小引數", "尺寸查詢表／size_lookup，核對原公式", "功能核對", "C19、S13"),
    ("C20", "重新整理", "僅重查既有干涉報告；完整複查須重新執行", "功能核對", "C20、S14；僅適用干涉報告語境"),
    ("P01", "\ufffd", "原始字幕替代字元，須聽音", "待確認", "P01"),
    ("P02", "1200", "視圖範圍欄位、單位與基準待畫面確認", "待確認", "P02；僅 M08 語境"),
    ("P04", "TOPFLO|TOPFNO|BOPFLO", "高程指示文字待原畫面確認", "待確認", "P04"),
    ("P05", "管號水|管號計算|兩層|耗手", "耗損欄位／比例待公式畫面確認", "待確認", "P05；僅 M35 語境"),
    ("P08", "徑環空水|迴圈風水", "系統名稱辨識不清，不作固定系統名", "待確認", "P08"),
    ("P09", "cns65|美亞攤鋼|無牙炭鋼", "材料／規格完整名稱待產品與畫面核對", "待確認", "P09"),
    ("P10", "80位", "封閉型路徑／設備名稱待畫面核對", "待確認", "P10"),
]


def read_cues(path: Path) -> list[tuple[str, str, str]]:
    """Read validated SRT blocks and keep the original cue text."""
    result = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = block.splitlines()
        if len(lines) < 3 or not lines[0].isdigit() or " --> " not in lines[1]:
            raise ValueError(f"Invalid SRT: {path}")
        start, end = lines[1].split(" --> ")
        result.append((start, end, "\n".join(lines[2:])))
    return result


def local_link(path: Path) -> str:
    """Return a portable relative URI for a file within the shared project."""
    return quote(Path("..", path.relative_to(ROOT)).as_posix(), safe="/:#")


def csv_write(path: Path, rows: list[list[object]]) -> None:
    buf = io.StringIO(newline="")
    csv.writer(buf).writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8-sig", newline="")


def collect_sources() -> list[dict[str, object]]:
    sources = []
    mep_videos = sorted(MEP.glob("*.mp4"), key=lambda path: path.name)
    revit_videos = [REVIT / f"{name}.mp4" for name in R_ORDER]
    if len(mep_videos) != 46 or set(revit_videos) != set(REVIT.glob("*.mp4")):
        raise ValueError("The source video inventory has changed.")
    for prefix, videos in [("M", mep_videos), ("R", revit_videos)]:
        for number, video in enumerate(videos, 1):
            stem = video.stem.removesuffix("_字幕").strip()
            matches = [s for s in video.parent.glob("*.srt") if s.stem.strip() == stem]
            if len(matches) != 1:
                raise ValueError(f"Subtitle mapping failed: {video}")
            srt = matches[0]
            plain = video.parent / "逐字稿" / f"{stem}_逐字稿.txt"
            timed = video.parent / "逐字稿" / f"{stem}_時間碼逐字稿.md"
            if not plain.exists() or not timed.exists():
                raise FileNotFoundError(f"Missing transcript: {video}")
            sources.append({
                "id": f"{prefix}{number:02d}", "video": video, "srt": srt,
                "plain": plain, "timed": timed, "cues": read_cues(srt),
                "sha256": hashlib.sha256(srt.read_bytes()).hexdigest(),
            })
    return sources


def enrich_books(sources: list[dict[str, object]]) -> None:
    lookup = {item["id"]: item for item in sources}
    for prefix, path in BOOKS.items():
        content = path.read_text(encoding="utf-8-sig")
        # Source notes and the unit navigation are generated idempotently.
        content = re.sub(r"<!-- unit-nav:start -->.*?<!-- unit-nav:end -->\n*", "", content, flags=re.S)
        content = re.sub(r'<a id="[mr]\d{2}"></a>\n', "", content)
        content = re.sub(r"\n來源影片：.*\n", "\n", content)
        lines, units = [], []
        pattern = re.compile(r"^### (M\d{2})　(.+)$" if prefix == "M" else r"^## 第 \d+ 章　(R\d{2}) (.+)$")
        for line in content.splitlines():
            match = pattern.match(line)
            if match:
                unit, title = match.groups()
                item = lookup[unit]
                lines.append(f'<a id="{unit.lower()}"></a>')
                lines.append(line)
                video, timed = item["video"], item["timed"]
                lines.extend(["", f"來源影片：[{video.name}]({local_link(video)})｜[時間碼逐字稿]({local_link(timed)})"])
                units.append((unit, title))
            else:
                lines.append(line)
        wanted = [str(item["id"]) for item in sources if str(item["id"]).startswith(prefix)]
        if [unit for unit, _ in units] != wanted:
            raise ValueError(f"Chapter coverage failed: {path.name}")
        nav = ["<!-- unit-nav:start -->", "## 單元目錄", "", "| 單元 | 主題 |", "| --- | --- |"]
        nav.extend(f"| {unit} | [{title}](#{unit.lower()}) |" for unit, title in units)
        nav.extend(["", "<!-- unit-nav:end -->", ""])
        joined = "\n".join(lines) + "\n"
        first_chapter = joined.index("<a id=\"r01\"") if prefix == "R" else joined.index("## 第 1 章")
        joined = joined[:first_chapter] + "\n".join(nav) + "\n" + joined[first_chapter:]
        path.write_text(joined, encoding="utf-8-sig")


def build_indexes(sources: list[dict[str, object]]) -> tuple[int, int]:
    index = [["教材編號", "教材檔案", "原影片", "來源字幕", "純文字逐字稿", "時間碼逐字稿", "字幕結束時間", "字幕段數", "字幕SHA256"]]
    evidence = [["校正編號", "教材編號", "校正等級", "來源影片", "來源字幕", "出現字幕段數", "第一處開始", "第一處結束", "原句例子", "教材採用術語或說明", "功能依據或條件"]]
    counts = Counter()
    for item in sources:
        unit = str(item["id"])
        index.append([
            unit, BOOKS[unit[0]].name, item["video"], item["srt"], item["plain"], item["timed"],
            item["cues"][-1][1], len(item["cues"]), item["sha256"],
        ])
        for code, pattern, correction, status, basis in RULES:
            found = [cue for cue in item["cues"] if re.search(pattern, cue[2], flags=re.I)]
            if found:
                first = found[0]
                evidence.append([code, unit, status, item["video"], item["srt"], len(found), first[0], first[1], first[2], correction, basis])
                counts[status] += 1
    csv_write(OUT / "05_影片對照索引.csv", index)
    csv_write(OUT / "06_校正定位清單.csv", evidence)
    return len(index) - 1, len(evidence) - 1


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
ET.register_namespace("w", W)
ET.register_namespace("r", R)


def w(name: str, attrs: dict[str, str] | None = None) -> ET.Element:
    return ET.Element(f"{{{W}}}{name}", {f"{{{W}}}{key}": value for key, value in (attrs or {}).items()})


class WordDocument:
    """A small OOXML writer for headings, links, tables, and paginated text."""

    def __init__(self, source: Path) -> None:
        self.source = source
        self.document = w("document")
        self.body = ET.SubElement(self.document, f"{{{W}}}body")
        self.relationships: list[tuple[str, str, str, bool]] = []
        self.bookmark_count = 0

    def rel(self, kind: str, target: str, external: bool = False) -> str:
        rid = f"rId{len(self.relationships) + 1}"
        self.relationships.append((rid, kind, target, external))
        return rid

    def run(self, parent: ET.Element, value: str, link: bool = False, bold: bool = False) -> None:
        chunks = value.split("\n")
        for i, chunk in enumerate(chunks):
            run = ET.SubElement(parent, f"{{{W}}}r")
            props = ET.SubElement(run, f"{{{W}}}rPr")
            if link:
                props.append(w("rStyle", {"val": "Hyperlink"}))
            if bold:
                props.append(w("b"))
            if i:
                run.append(w("br"))
            text = ET.SubElement(run, f"{{{W}}}t", {"{http://www.w3.org/XML/1998/namespace}space": "preserve"})
            text.text = chunk

    def inline(self, parent: ET.Element, value: str, bold: bool = False) -> None:
        last = 0
        for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", value):
            self.run(parent, value[last:match.start()].replace("`", ""), bold=bold)
            label, target = match.groups()
            attrs = {}
            if target.startswith("#"):
                attrs[f"{{{W}}}anchor"] = target[1:]
            else:
                if not target.startswith(("http://", "https://")):
                    target = (self.source.parent / unquote(target)).resolve().as_uri()
                attrs[f"{{{R}}}id"] = self.rel("hyperlink", target, True)
            hyperlink = ET.SubElement(parent, f"{{{W}}}hyperlink", attrs)
            self.run(hyperlink, label, link=True, bold=bold)
            last = match.end()
        self.run(parent, value[last:].replace("`", ""), bold=bold)

    def paragraph(self, text: str, style: str = "Normal", parent: ET.Element | None = None, bookmark: str | None = None) -> ET.Element:
        p = ET.SubElement(self.body if parent is None else parent, f"{{{W}}}p")
        props = ET.SubElement(p, f"{{{W}}}pPr")
        props.append(w("pStyle", {"val": style}))
        if bookmark:
            number = str(self.bookmark_count)
            self.bookmark_count += 1
            p.append(w("bookmarkStart", {"id": number, "name": bookmark}))
            self.inline(p, text)
            p.append(w("bookmarkEnd", {"id": number}))
        else:
            self.inline(p, text)
        return p

    def table(self, rows: list[list[str]]) -> None:
        columns = len(rows[0])
        table = ET.SubElement(self.body, f"{{{W}}}tbl")
        props = ET.SubElement(table, f"{{{W}}}tblPr")
        props.append(w("tblW", {"w": "9638", "type": "dxa"}))
        props.append(w("tblLayout", {"type": "fixed"}))
        borders = ET.SubElement(props, f"{{{W}}}tblBorders")
        for name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
            borders.append(w(name, {"val": "single", "sz": "4", "color": "D0D8DF"}))
        if rows[0][0] == "編號" and columns == 3:
            widths = [850, 6800, 1988]
        elif rows[0][0] == "單元" and columns == 2:
            widths = [1100, 8538]
        else:
            widths = [9638 // columns] * columns
        grid = ET.SubElement(table, f"{{{W}}}tblGrid")
        for width in widths:
            grid.append(w("gridCol", {"w": str(width)}))
        for number, row in enumerate(rows):
            if len(row) != columns:
                raise ValueError(f"Uneven table in {self.source.name}: {row}")
            tr = ET.SubElement(table, f"{{{W}}}tr")
            row_props = ET.SubElement(tr, f"{{{W}}}trPr")
            row_props.append(w("cantSplit"))
            if number == 0:
                row_props.append(w("tblHeader"))
            for i, cell in enumerate(row):
                tc = ET.SubElement(tr, f"{{{W}}}tc")
                cp = ET.SubElement(tc, f"{{{W}}}tcPr")
                cp.append(w("tcW", {"w": str(widths[i]), "type": "dxa"}))
                if number == 0:
                    cp.append(w("shd", {"val": "clear", "color": "auto", "fill": "E7EEF5"}))
                elif number % 2 == 0:
                    cp.append(w("shd", {"val": "clear", "color": "auto", "fill": "F6F8FA"}))
                self.paragraph(cell, "TableHeader" if number == 0 else "TableText", tc)
        self.paragraph("")

    def parse(self, markdown: str) -> None:
        lines = markdown.splitlines()
        i, bookmark = 0, None
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            if not line or line.startswith("<!--"):
                continue
            anchor = re.fullmatch(r'<a id="([^"]+)"></a>', line)
            if anchor:
                bookmark = anchor[1]
                continue
            if line.startswith("|"):
                raw_rows = [line]
                while i < len(lines) and lines[i].strip().startswith("|"):
                    raw_rows.append(lines[i].strip())
                    i += 1
                rows = []
                for raw in raw_rows:
                    cells = [cell.strip() for cell in raw.strip("|").split("|")]
                    if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                        continue
                    rows.append(cells)
                self.table(rows)
                continue
            heading = re.match(r"^(#{1,4})\s+(.+)$", line)
            if heading:
                level = len(heading[1])
                self.paragraph(heading[2], "Title" if level == 1 else f"Heading{level - 1}", bookmark=bookmark)
                bookmark = None
                continue
            if line.startswith("來源影片："):
                style = "Source"
            elif re.match(r"^\d+\. ", line):
                style = "Step"
            elif line.startswith("- "):
                style, line = "Step", "• " + line[2:]
            else:
                style = "Normal"
            self.paragraph(line, style)

    def save(self, target: Path) -> None:
        styles_id = self.rel("styles", "styles.xml")
        footer_id = self.rel("footer", "footer1.xml")
        header_id = self.rel("header", "header1.xml")
        del styles_id
        section = ET.SubElement(self.body, f"{{{W}}}sectPr")
        ET.SubElement(section, f"{{{W}}}headerReference", {f"{{{W}}}type": "default", f"{{{R}}}id": header_id})
        ET.SubElement(section, f"{{{W}}}footerReference", {f"{{{W}}}type": "default", f"{{{R}}}id": footer_id})
        section.append(w("pgSz", {"w": "11906", "h": "16838"}))
        section.append(w("pgMar", {"top": "1134", "right": "1134", "bottom": "1134", "left": "1134", "header": "567", "footer": "567", "gutter": "0"}))
        rels = ET.Element(f"{{{REL}}}Relationships")
        for rid, kind, href, external in self.relationships:
            attrs = {"Id": rid, "Type": f"{R}/{kind}", "Target": href}
            if external:
                attrs["TargetMode"] = "External"
            ET.SubElement(rels, f"{{{REL}}}Relationship", attrs)
        header = w("hdr")
        self.paragraph("Revit 2025 繁體中文教材　｜　" + self.source.stem[3:], "Header", header)
        footer = w("ftr")
        fp = self.paragraph("2026-10-24　｜　第 ", "Footer", footer)
        field = ET.SubElement(fp, f"{{{W}}}fldSimple", {f"{{{W}}}instr": " PAGE "})
        self.run(field, "1")
        self.run(fp, " 頁")
        ns = "http://schemas.openxmlformats.org/package/2006/content-types"
        types = ET.Element(f"{{{ns}}}Types")
        ET.SubElement(types, f"{{{ns}}}Default", {"Extension": "rels", "ContentType": "application/vnd.openxmlformats-package.relationships+xml"})
        ET.SubElement(types, f"{{{ns}}}Default", {"Extension": "xml", "ContentType": "application/xml"})
        for part, mime in [("document", "document.main"), ("styles", "styles"), ("header1", "header"), ("footer1", "footer")]:
            ET.SubElement(types, f"{{{ns}}}Override", {"PartName": f"/word/{part}.xml", "ContentType": f"application/vnd.openxmlformats-officedocument.wordprocessingml.{mime}+xml"})
        root_rels = ET.Element(f"{{{REL}}}Relationships")
        ET.SubElement(root_rels, f"{{{REL}}}Relationship", {"Id": "rId1", "Type": f"{R}/officeDocument", "Target": "word/document.xml"})
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as package:
            for name, element in [
                ("[Content_Types].xml", types), ("_rels/.rels", root_rels),
                ("word/document.xml", self.document), ("word/_rels/document.xml.rels", rels),
                ("word/header1.xml", header), ("word/footer1.xml", footer),
            ]:
                package.writestr(name, ET.tostring(element, encoding="utf-8", xml_declaration=True))
            package.writestr("word/styles.xml", styles_xml())


def styles_xml() -> bytes:
    styles = w("styles")
    defaults = ET.SubElement(styles, f"{{{W}}}docDefaults")
    rp = ET.SubElement(ET.SubElement(defaults, f"{{{W}}}rPrDefault"), f"{{{W}}}rPr")
    rp.append(w("rFonts", {"ascii": "Calibri", "hAnsi": "Calibri", "eastAsia": "Microsoft JhengHei"}))
    rp.append(w("sz", {"val": "22"}))
    rp.append(w("lang", {"val": "en-US", "eastAsia": "zh-TW"}))
    pp = ET.SubElement(ET.SubElement(defaults, f"{{{W}}}pPrDefault"), f"{{{W}}}pPr")
    pp.append(w("spacing", {"after": "120", "line": "324", "lineRule": "auto"}))
    definitions = [
        ("Normal", "Normal", 22, None, False), ("Title", "Title", 40, "18364E", True),
        ("Heading1", "heading 1", 29, "18364E", True),
        ("Heading2", "heading 2", 25, "234F70", True),
        ("Heading3", "heading 3", 23, "234F70", True),
        ("TableText", "Table Text", 18, None, False),
        ("TableHeader", "Table Header", 18, "18364E", True),
        ("Step", "Step", 22, None, False), ("Source", "Source", 18, "546574", False),
        ("Header", "Header", 16, "546574", False), ("Footer", "Footer", 16, "546574", False),
    ]
    for sid, name, size, color, bold in definitions:
        st = w("style", {"type": "paragraph", "styleId": sid})
        if sid == "Normal":
            st.set(f"{{{W}}}default", "1")
        st.append(w("name", {"val": name}))
        if sid != "Normal":
            st.append(w("basedOn", {"val": "Normal"}))
        ppr = ET.SubElement(st, f"{{{W}}}pPr")
        if sid.startswith("Heading") or sid == "Title":
            ppr.append(w("keepNext"))
            ppr.append(w("spacing", {"before": "280", "after": "140"}))
        if sid.startswith("Heading"):
            ppr.append(w("outlineLvl", {"val": str(int(sid[-1]) - 1)}))
        if sid == "Step":
            ppr.append(w("ind", {"left": "280", "hanging": "280"}))
        if sid in {"TableText", "TableHeader", "Source"}:
            ppr.append(w("spacing", {"after": "60", "line": "276", "lineRule": "auto"}))
        if sid in {"Header", "Footer"}:
            ppr.append(w("jc", {"val": "center"}))
        ppr.append(w("widowControl"))
        rpr = ET.SubElement(st, f"{{{W}}}rPr")
        rpr.append(w("sz", {"val": str(size)}))
        if color:
            rpr.append(w("color", {"val": color}))
        if bold:
            rpr.append(w("b"))
        styles.append(st)
    hyperlink = w("style", {"type": "character", "styleId": "Hyperlink"})
    hyperlink.append(w("name", {"val": "Hyperlink"}))
    pr = ET.SubElement(hyperlink, f"{{{W}}}rPr")
    pr.append(w("color", {"val": "146C94"}))
    pr.append(w("u", {"val": "single"}))
    styles.append(hyperlink)
    return ET.tostring(styles, encoding="utf-8", xml_declaration=True)


def verify(sources: list[dict[str, object]]) -> dict[str, object]:
    for item in sources:
        if hashlib.sha256(item["srt"].read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("A source subtitle changed during processing.")
    markdowns = sorted(OUT.glob("0[0-4]_*.md"))
    if len(markdowns) != 5:
        raise ValueError("Expected five teaching documents.")
    broken, timings = [], 0
    for path in markdowns:
        content = path.read_text(encoding="utf-8-sig")
        for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content):
            if target.startswith(("http://", "https://", "#")):
                continue
            if not (path.parent / unquote(target)).resolve().exists():
                broken.append((path.name, label, target))
        if "\ufffd" in content:
            # The correction register legitimately discusses the original damaged cue.
            raise ValueError(f"Unexpected replacement character in material: {path.name}")
    if broken:
        raise ValueError(f"Broken links: {broken}")
    advanced = BOOKS["R"].read_text(encoding="utf-8-sig")
    for number in [9, 10, 11]:
        unit = f"R{number:02d}"
        body = re.split(rf"^## 第 {number} 章", advanced, flags=re.M)[1]
        if number < 11:
            body = body.split(f"## 第 {number + 1} 章")[0]
        source = next(item for item in sources if item["id"] == unit)
        starts = {cue[0].split(",")[0] for cue in source["cues"]}
        for timing in re.findall(r"^\| (\d{2}:\d{2}:\d{2}) \|", body, flags=re.M):
            if timing not in starts:
                raise ValueError(f"Unmatched replay time: {unit} {timing}")
            timings += 1
    for md in markdowns:
        docx = md.with_suffix(".docx")
        with zipfile.ZipFile(docx) as package:
            if package.testzip() is not None:
                raise ValueError(f"Invalid ZIP: {docx}")
            for name in package.namelist():
                if name.endswith((".xml", ".rels")):
                    ET.fromstring(package.read(name))
            xml = ET.fromstring(package.read("word/document.xml"))
            text = "".join(el.text or "" for el in xml.iter(f"{{{W}}}t"))
            if len(text) < 500:
                raise ValueError(f"Empty document: {docx}")
            expected_units = re.findall(r'^<a id="([mr]\d{2})"></a>$', md.read_text(encoding="utf-8-sig"), flags=re.M)
            anchors = [el.attrib[f"{{{W}}}name"] for el in xml.iter(f"{{{W}}}bookmarkStart")]
            if anchors != expected_units:
                raise ValueError(f"Bookmark coverage failed: {docx}")
            doc_text = re.sub(r"[\s`]+", "", text)
            for line in md.read_text(encoding="utf-8-sig").splitlines():
                if not line.strip() or line.startswith(("<!--", "<a ")):
                    continue
                line = re.sub(r"^#{1,4}\s+", "", line).strip()
                if line.startswith("|"):
                    cells = [cell.strip() for cell in line.strip("|").split("|")]
                    if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                        continue
                else:
                    cells = [line.removeprefix("- ")]
                for cell in cells:
                    cell = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cell)
                    cell = re.sub(r"[\s`]+", "", cell)
                    if cell and cell not in doc_text:
                        raise ValueError(f"Text omitted from Word: {md.name}: {cell[:60]}")
    return {"source_videos": len(sources), "source_cues": sum(len(item["cues"]) for item in sources), "teaching_documents": len(markdowns), "replay_times_verified": timings, "broken_local_links": len(broken), "source_subtitles_unchanged": True, "word_package_xml_and_text_checked": True, "revit_live_validation": False, "word_visual_validation": False}


def main() -> None:
    sources = collect_sources()
    enrich_books(sources)
    videos, evidence = build_indexes(sources)
    for md in sorted(OUT.glob("0[0-4]_*.md")):
        document = WordDocument(md)
        document.parse(md.read_text(encoding="utf-8-sig"))
        document.save(md.with_suffix(".docx"))
    result = verify(sources)
    result["evidence_rows"] = evidence
    result["inventory_rows"] = videos
    (OUT / "工具" / "檢核結果.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
