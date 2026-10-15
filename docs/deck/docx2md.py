"""Dump a .docx to rough markdown using only the stdlib: headings, paragraphs,
list levels, tables, and image placeholders. Extracts media alongside."""
import sys, zipfile, os, re
import xml.etree.ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
ns = {"w": W, "r": R, "a": A}

src, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
z = zipfile.ZipFile(src)

rels = {}
for rel in ET.fromstring(z.read("word/_rels/document.xml.rels")).findall(f"{{{REL}}}Relationship"):
    rels[rel.get("Id")] = rel.get("Target")

media_dir = os.path.join(out_dir, "media")
os.makedirs(media_dir, exist_ok=True)
for name in z.namelist():
    if name.startswith("word/media/"):
        with open(os.path.join(media_dir, os.path.basename(name)), "wb") as f:
            f.write(z.read(name))

# style id -> name, so custom heading ids resolve
styles = {}
if "word/styles.xml" in z.namelist():
    for s in ET.fromstring(z.read("word/styles.xml")).findall("w:style", ns):
        n = s.find("w:name", ns)
        styles[s.get(f"{{{W}}}styleId")] = n.get(f"{{{W}}}val") if n is not None else ""


def para_text(p):
    parts = []
    for node in p.iter():
        tag = node.tag
        if tag == f"{{{W}}}t":
            parts.append(node.text or "")
        elif tag == f"{{{W}}}tab":
            parts.append("\t")
        elif tag in (f"{{{W}}}br", f"{{{W}}}cr"):
            parts.append(" / ")
        elif tag == f"{{{A}}}blip":
            rid = node.get(f"{{{R}}}embed")
            parts.append(f"[IMAGE: {os.path.basename(rels.get(rid, rid or '?'))}]")
    return "".join(parts)


def render_para(p):
    ppr = p.find("w:pPr", ns)
    style, ilvl, is_list = "", 0, False
    if ppr is not None:
        ps = ppr.find("w:pStyle", ns)
        if ps is not None:
            style = styles.get(ps.get(f"{{{W}}}val"), ps.get(f"{{{W}}}val"))
        num = ppr.find("w:numPr", ns)
        if num is not None:
            is_list = True
            lv = num.find("w:ilvl", ns)
            ilvl = int(lv.get(f"{{{W}}}val")) if lv is not None else 0
    text = para_text(p).strip()
    if not text:
        return None
    m = re.match(r"(?i)heading\s*(\d)", style or "")
    if m:
        return "#" * int(m.group(1)) + " " + text
    if (style or "").lower() == "title":
        return "# [TITLE] " + text
    if is_list or "list" in (style or "").lower():
        return "  " * ilvl + "- " + text
    return text


def render_table(tbl):
    rows = []
    for tr in tbl.findall("w:tr", ns):
        cells = []
        for tc in tr.findall("w:tc", ns):
            cell = " ".join(filter(None, (para_text(p).strip() for p in tc.iter(f"{{{W}}}p"))))
            cells.append(cell.replace("|", "\\|"))
        rows.append("| " + " | ".join(cells) + " |")
    if rows:
        ncol = rows[0].count("|") - 1
        rows.insert(1, "|" + "---|" * ncol)
    return "\n".join(rows)


body = ET.fromstring(z.read("word/document.xml")).find("w:body", ns)
lines = []
for child in body:
    if child.tag == f"{{{W}}}p":
        r = render_para(child)
        if r:
            lines.append(r)
    elif child.tag == f"{{{W}}}tbl":
        lines.append("\n[TABLE]\n" + render_table(child) + "\n")
    elif child.tag == f"{{{W}}}sdt":  # content controls (e.g. TOC)
        for p in child.iter(f"{{{W}}}p"):
            r = render_para(p)
            if r:
                lines.append(r)

with open(os.path.join(out_dir, "draft.md"), "w", encoding="utf-8") as f:
    f.write("\n\n".join(lines))

# comments, if any
if "word/comments.xml" in z.namelist():
    cs = ET.fromstring(z.read("word/comments.xml")).findall("w:comment", ns)
    with open(os.path.join(out_dir, "comments.md"), "w", encoding="utf-8") as f:
        for c in cs:
            f.write(f"- [{c.get(f'{{{W}}}author')}] " + " ".join(para_text(p) for p in c.iter(f"{{{W}}}p")) + "\n")
    print(f"comments: {len(cs)}")
print("parts:", [n for n in z.namelist() if not n.startswith("word/media/")])
