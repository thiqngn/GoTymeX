"""Build the walkthrough deck as .pptx with python-pptx, mirroring the artifact slides."""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

OUT = sys.argv[1]
FIG = sys.argv[2].rstrip("/\\") + "/"

W, H = 13.333, 7.5
S = W / 1920.0  # inches per design pixel

def px(n): return Inches(n * S)
def pt(n): return Pt(n * 0.5)  # 1920px canvas at 13.33in: 1px ≈ 0.5pt

NAVY = RGBColor(0x15, 0x22, 0x3A); OFF = RGBColor(0xF6, 0xF3, 0xEC)
ORANGE = RGBColor(0xE3, 0x8B, 0x3A); TEAL = RGBColor(0x1F, 0x6F, 0x8B)
BODY = RGBColor(0x3C, 0x46, 0x56); MUTED = RGBColor(0x6B, 0x74, 0x84)
WHITE = RGBColor(0xFF, 0xFF, 0xFF); LINE = RGBColor(0xDE, 0xD8, 0xCC)
PALE = RGBColor(0xBF, 0xC9, 0xDA); ROW = RGBColor(0xFB, 0xF9, 0xF4)
DK2 = RGBColor(0x1E, 0x2D, 0x48); DK3 = RGBColor(0x1A, 0x28, 0x43)
HEAD, TEXT = "Cambria", "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]


def bg(slide, color):
    f = slide.background.fill; f.solid(); f.fore_color.rgb = color


def text(slide, s, x, y, w, h, size, color=BODY, bold=False, font=TEXT, align=PP_ALIGN.LEFT,
         italic=False, anchor=MSO_ANCHOR.TOP, runs=None, line=1.2):
    tb = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]; p.alignment = align; p.line_spacing = line
    for (t, b) in (runs or [(s, bold)]):
        r = p.add_run(); r.text = t
        r.font.size = pt(size); r.font.bold = b; r.font.italic = italic
        r.font.color.rgb = color; r.font.name = font
    return tb


def para_box(slide, items, x, y, w, h, size, color=BODY, font=TEXT, gap=10, bullets=False):
    tb = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    first = True
    for item in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        p.line_spacing = 1.2; p.space_after = pt(gap)
        runs = item if isinstance(item, list) else [(item, False)]
        if bullets:
            runs = [("•  ", False)] + runs
        for t, b in runs:
            r = p.add_run(); r.text = t; r.font.size = pt(size); r.font.bold = b
            r.font.color.rgb = color; r.font.name = font
    return tb


def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE):
    sh = slide.shapes.add_shape(shape, px(x), px(y), px(w), px(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb = line; sh.line.width = Pt(0.75)
    sh.shadow.inherit = False
    return sh


def img(slide, name, x, y, w, h):
    """Place figure 'name' contained in the box, on a white panel."""
    rect(slide, x, y, w, h, WHITE, LINE)
    iw, ih = Image.open(FIG + name).size
    scale = min((w - 24) / iw, (h - 24) / ih)
    dw, dh = iw * scale, ih * scale
    slide.shapes.add_picture(FIG + name, px(x + (w - dw) / 2), px(y + (h - dh) / 2), px(dw), px(dh))


def heading(slide, s, dark=False):
    text(slide, s, 128, 128, 1664, 150, 60, color=OFF if dark else NAVY, bold=True, font=HEAD, line=1.1)


def footer(slide, n, caption=None, dark=False):
    c = PALE if dark else MUTED
    if caption:
        text(slide, caption, 128, 1016 - 30, 1400, 34, 22, color=c)
    text(slide, str(n), 1732, 1016 - 30, 60, 34, 22, color=c, align=PP_ALIGN.RIGHT)


def card(slide, title, body, x, y, w, h, title_color=NAVY, size=24):
    rect(slide, x, y, w, h, WHITE, LINE)
    text(slide, title, x + 28, y + 24, w - 56, 40, 28, color=title_color, bold=True)
    text(slide, body, x + 28, y + 70, w - 56, h - 90, size, color=BODY, line=1.25)


def notes(slide, s):
    slide.notes_slide.notes_text_frame.text = s


# ---------- 1 cover ----------
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
text(s, "PERSONAL LOAN  ·  DATA PLATFORM, DATA MODEL AND DECISION LOG", 128, 128, 1664, 40, 24, color=ORANGE, bold=True)
text(s, "Lending Analytics Design", 128, 380, 1664, 150, 110, color=OFF, bold=True, font=HEAD, line=1.05)
text(s, "Four services, four databases, nothing enforces the join. One append-only capture path, as-of history, and an honest answer to every question.",
     128, 560, 1300, 160, 38, color=PALE, line=1.3)
text(s, "Walkthrough of the submitted design", 128, 900, 1000, 40, 26, color=PALE)
text(s, "October 2026", 1400, 900, 392, 40, 26, color=PALE, align=PP_ALIGN.RIGHT)
notes(s, "Open with the one-sentence frame: Four services, four databases, nothing enforces the join. I built one append-only capture path, turned it into as-of history, and put every question on top of that history, so the platform can always say what it knew, when it knew it, and what it did not capture. Three words to remember: append-only, as-of, honest. Then: Twelve minutes, thirteen slides in five sections, and I will stop wherever you want to dig.")

# ---------- 2 frame ----------
s = prs.slides.add_slide(BLANK); bg(s, OFF)
heading(s, "Four databases, one shared value, nothing enforces it")
img(s, "image1.png", 230, 230, 1460, 650)
footer(s, 2, "Figure 1 in the document. The application number travels under two column names.")
notes(s, "Four MySQL databases, three teams, REST and Kafka between them. The application number is the only value all four carry, under two column names, and nothing enforces it. Every cross-service join used to live in application code. The design moves it into the platform, once, with evidence of where every value came from. Everything else in the document exists to answer one of four questions, which come next.")

# ---------- 3 questions ----------
s = prs.slides.add_slide(BLANK); bg(s, OFF)
heading(s, "Four questions, and what each one really tests")
rows = [("Q", "The brief asks", "What it tests"),
        ("Q1", "Share of a month’s submissions funded within 14 days, by channel, and why the rest did not fund", "A cohort that never moves, a reason that always sums"),
        ("Q2", "Reconstruct the inputs the credit engine saw at decision time, even if the sources have since changed", "History that is captured, never reconstructed"),
        ("Q3", "Each morning: offers expiring in 24 hours and unaccepted, plus offers expired without action in 7 days", "An operational list with a record of what ops was told"),
        ("Q4", "Prove to a regulator that PII was masked before any analyst touched the funnel data for a quarter", "Evidence, not configuration")]
tbl = s.shapes.add_table(len(rows), 3, px(128), px(260), px(1664), px(520)).table
tbl.columns[0].width = px(130); tbl.columns[1].width = px(840); tbl.columns[2].width = px(694)
tbl.rows[0].height = px(70)
for i in range(1, len(rows)): tbl.rows[i].height = px(110)
for i, row in enumerate(rows):
    for j, val in enumerate(row):
        c = tbl.cell(i, j); c.text = ""
        c.fill.solid(); c.fill.fore_color.rgb = NAVY if i == 0 else (WHITE if i % 2 else ROW)
        c.margin_left = c.margin_right = px(24); c.margin_top = c.margin_bottom = px(16)
        p = c.text_frame.paragraphs[0]; r = p.add_run(); r.text = val
        r.font.name = TEXT; r.font.size = pt(28)
        r.font.bold = (i == 0 or j == 0)
        r.font.color.rgb = OFF if i == 0 else (ORANGE if j == 0 else BODY)
text(s, "", 128, 820, 1664, 80, 28, runs=[("Three words carry the whole design: ", False), ("append-only", True), (" capture, ", False), ("as-of", True), (" reads, and an ", False), ("honest", True), (" answer that says what was not captured.", False)], line=1.3)
footer(s, 3)
notes(s, "Read the right-hand column, not the left. Q1 tests whether a cohort can be pinned so a rewrite cannot move it, and whether the drop-off reasons sum to the cohort. Q2 is only answerable with append-only capture: the phrase even if the sources have since changed rules out reading current rows. Q3 is a morning SLA, not analytics, and the list itself becomes a record. Q4 asks for proof after the fact, so the answer is evidence tables, not a description of masks.")

# ---------- 4 pipeline ----------
s = prs.slides.add_slide(BLANK); bg(s, OFF)
heading(s, "One capture path feeds both speeds, so they cannot disagree")
img(s, "image2.png", 128, 300, 1080, 540)
y0 = 300
for t, b, col in [("Capture", "DMS reads each writer’s binlog into one-minute S3 files. Bronze is an append-only change log, full refresh blocked.", ORANGE),
                  ("Daily route", "Silver and Gold are one dbt project, rebuilt from Bronze at 05:00, tunable to 30 minutes.", TEAL),
                  ("Minutes route", "One stream reads the same landing files. Nothing is real-time unless a question needs it.", NAVY)]:
    card(s, t, b, 1248, y0, 544, 190, title_color=col); y0 += 206
footer(s, 4, "Figure 2 in the document. Orange marks where clear identifiers may live: landing, Bronze, restricted.")
notes(s, "Stress: the daily build and the alert stream read the same landing files, so they cannot disagree about what happened. Nothing is real-time unless a question needs it, and only one does: a failed disbursement, and money moving after a DECLINED decision. Why DMS over the services’ existing Kafka CDC topics: reuse is the strongest alternative and I say so, but I could not confirm six things about those topics; any one missing means no history for Silver. DMS until an owner confirms, then Bronze reads the topics and nothing downstream changes. Why dbt though it is outside the brief’s stack: same warehouse and catalog, so no new engine to govern; masks and tags live with each model; the volume makes a full daily rebuild cheap, which is what makes a fix reaches all of history tomorrow true.")

# ---------- 5 stream ----------
s = prs.slides.add_slide(BLANK); bg(s, OFF)
heading(s, "The one stream: record the alert first, then send it")
img(s, "image3.png", 128, 290, 1664, 420)
x0 = 128
for t, b in [("Outbox", "The alert table is the outbox. A crash between record and send never loses an alert."),
             ("Deterministic id", "Disbursement id, change sequence and rule. A replay sends the same id; the receiver drops the duplicate."),
             ("Backstop", "The daily build re-tests every disbursement, so anything the stream misses is caught by morning.")]:
    card(s, t, b, x0, 740, 533, 200, title_color=ORANGE); x0 += 565
footer(s, 5, "Figure 3 in the document. Kafka is the target until ops confirms what its tooling reads.")
notes(s, "Two rules: a FAILED disbursement because a customer is waiting for money, and money moving on an application whose latest decision is DECLINED, the most serious disagreement in the design. Latency is one-minute files plus a one-minute trigger, typically one to three minutes, inside a five-minute target. Health: a heartbeat each time the stream checks for work, so a quiet night is not mistaken for a fault. I rejected Flink and Spark real-time mode: seconds of latency where ops acts in minutes, and a second engine outside the catalog’s audit. The pattern scales: each new stream reads the same landing files and writes its own outbox.")

# ---------- 6 history ----------
s = prs.slides.add_slide(BLANK); bg(s, OFF)
heading(s, "History is captured, never reconstructed, and a gap says so")
img(s, "image4.png", 128, 300, 1000, 440)
para_box(s, [[("One source row, three versions. ", True), ("Nothing in Bronze is updated or deleted. Silver gives each version a valid-from and valid-to, and every as-of read in the design uses the same predicate.", False)],
             [("A capture gap is data. ", True), ("A read inside it returns NOT_CAPTURED, a cohort over it freezes as HELD, and the funnel starts at the first month with no gap.", False)],
             [("One hard failure only. ", True), ("A contracted column that disappears or changes type fails the run. An unknown enum becomes UNMAPPED, still sums, and is published as a contract violation.", False)]],
         1168, 300, 624, 640, 26, gap=18)
footer(s, 6, "Figure 4 in the document.")
notes(s, "This slide is why Q2 is answerable at all. A loan_offer row is unique per application and overwritten in place, so its history exists only in the change log. Say the cost out loud: anything before the first captured image is NOT_CAPTURED and labelled so; I did not pretend to reconstruct it. The capture columns are the operation, the source commit time, the change sequence, the load type, the source file, the ingestion time, and a rescued-data column that makes a type change visible instead of silent.")

# ---------- 7 boundary ----------
s = prs.slides.add_slide(BLANK); bg(s, OFF)
heading(s, "Direct identifiers stop at one macro, one function, one principal")
img(s, "image18.png", 128, 310, 1664, 420)
x0 = 128
for t, b in [("One macro", "builds all nineteen history tables and replaces national_id with a keyed hash. No analyst-readable table has ever held a direct identifier."),
             ("One function", "HMAC-SHA-256 with a key version, that only the transform principal can run. Nobody else can compute the key for a chosen id."),
             ("Rotation is a rebuild.", "Silver is rebuilt from Bronze every morning anyway, so a new key is a re-key, not a migration.")]:
    text(s, "", x0, 760, 533, 190, 25, runs=[(t + " ", True), (b, False)], line=1.25); x0 += 565
footer(s, 7, "Figure 17 in the document (section 6.1). Names, mobile, email and date of birth go clear to the restricted schema only.")
notes(s, "This is the point that makes Q4 easy. Because the boundary is one macro, the fields the brief names never reach an analyst-readable table, so the regulator proof is an absence proof plus access evidence, not a masking audit. Rejected: unkeyed SHA-256, because a small structured id space can be enumerated; a token vault, because the mapping table is a second store of clear identifiers to guard, back up, erase and evidence. Erasure: retention wins for raw data and decision records; the analytical layers remove the bridge and identity rows, null personal attributes, and vacuum seven days of table history. Frozen cohorts carry no person at all.")

# ---------- 8 star ----------
s = prs.slides.add_slide(BLANK); bg(s, OFF)
heading(s, "Gold is a plain star, and beside it, records of what someone was shown")
img(s, "image8.png", 128, 300, 1080, 520)
para_box(s, [[("Three facts, five dimensions, no stored aggregates. ", True), ("Every number is a join and a group by. Metrics are code-owned views, so Product owns a definition by owning a file.", False)],
             [("Keys are the business codes. ", True), ("Channel, branch, product, the bank-local date. A join reads the way a business user says it.", False)],
             [("Written once, never edited: ", True), ("the frozen cohort, the decision input record, the morning watchlist, the gate verdict. A frozen row stores names as text, so it never depends on a dimension that changes later.", False)]],
         1248, 300, 544, 640, 25, gap=16)
footer(s, 8, "Figure 8 in the document.")
notes(s, "The facts: one row per submitted application, one per disbursement with a negative row per reversal, one per whitelist entry, for whitelist-to-application conversion. The dimensions include a versioned drop-off bucket mapping, so the roll-up from fine outcome codes to the brief’s five reasons is a seed Product can change with a diff, not logic. The written-once records are the part to stress: what a regulator was shown, what compliance was shown, what ops was told each morning, and whether a cohort was allowed to publish, each a row that cannot be edited afterwards.")

# ---------- 9 q1 ----------
s = prs.slides.add_slide(BLANK); bg(s, OFF)
heading(s, "Q1 · A cohort is pinned, frozen at maturity, and gated before it publishes")
img(s, "image10.png", 128, 300, 850, 650)
y0 = 300
for t, b in [("Pinned", "The cohort is keyed on the first submission ever captured. A rewrite of submitted_at cannot move an application between months."),
             ("One reason that always sums", "The first exit after the last re-entry on one cross-service timeline, read at day 14. Funded, five buckets and in-progress add up to the cohort."),
             ("Freeze, diff, gate", "A mature cohort is written once. Today’s recompute is diffed against it. Two thresholds: the Lending squad sets flag, Product sets hold. A held cohort publishes a HELD row, never silence.")]:
    card(s, t, b, 1018, y0, 774, 200, title_color=ORANGE, size=23); y0 += 224
footer(s, 9, "Figure 10 in the document. Values are illustrative.")
notes(s, "Walk the picture top to bottom: cohort size, funded share frozen beside recomputed, outcome mix by channel, then why the rest did not fund, each of the brief’s five reasons as a share of the cohort and of the unfunded. Say illustrative once and do not linger on the arithmetic. The join at answer time is the funnel fact and two dimensions; the fact itself is built once a day from six source tables, every join as of commit time against history. Corrections are versioned restatements with a reason, and the roll-up mapping is versioned with a change reason and an approver.")

# ---------- 10 q2 ----------
s = prs.slides.add_slide(BLANK); bg(s, OFF)
heading(s, "Q2 · The platform proves what the sources held, and says what it cannot prove")
img(s, "image12.png", 128, 300, 1080, 520)
para_box(s, [[("Each input read as of its own time ", True), ("from the history tables, with an evidence grade: engine copy, source as of, or not captured.", False)],
             [("Ambiguity is a flag, not a guess. ", True), ("Two bureau fetches in the read window flag the bureau input. A late input opens a new record version; the old one stays.", False)],
             [("Re-derived weekly ", True), ("against a stored hash. A mismatch is published as a defect, never corrected. Legacy decisions are served as they are, graded NOT_CAPTURED.", False)]],
         1248, 300, 544, 640, 25, gap=16)
footer(s, 10, "Figure 12 in the document. Values are illustrative.")
notes(s, "Say the boundary out loud; it is the strongest thing in Q2: the platform proves what the sources held and what the engine copied onto its decision row. It cannot prove what the engine actually read unless the engine says so. That is where the confirm item comes from: ask the decision service for an inputs snapshot event keyed on application number and decision version. The decision row already copies the employer fields, so the rest is a small step, and it lifts every answer to the top evidence grade. Declared income has two homes and which one the engine used is open; the record carries both with their read times.")

# ---------- 11 q3q4 ----------
s = prs.slides.add_slide(BLANK); bg(s, OFF)
heading(s, "Q3 and Q4 · An operational list that is a record, and a proof that is evidence")
img(s, "image14.png", 128, 300, 812, 420); img(s, "image16.png", 980, 300, 812, 420)
text(s, "Q3 · Offer expiry watchlist", 128, 740, 812, 40, 28, color=ORANGE, bold=True)
text(s, "The offer is read by version, because the row is overwritten in place. Acceptance is an anti-join at the data cut-off. Expiry-pending offers lead the list, since a customer can still accept until the expiry job runs. Each morning’s list is snapshotted: what ops was told is a record.",
     128, 788, 812, 180, 23, line=1.25)
text(s, "Q4 · Proof that PII was masked", 980, 740, 812, 40, 28, color=ORANGE, bold=True)
text(s, "Six evidence tables, none of them business data, exported daily to a write-once bucket in a security-owned account. A probe principal reads masked columns every day and tries the forbidden layers. Break-glass reads join to their ticket.",
     980, 788, 812, 170, 23, line=1.25)
footer(s, 11, "Figures 14 and 16 in the document. Values and counts are illustrative.")
notes(s, "Q3: the open-offer test is explicit because an accepted offer never expires in the data; without it every accepted offer would top the list each morning. Names and mobiles come from the restricted schema through one view, for ops only. Q4: the short answer is that the fields the brief names never reach an analyst-readable table, so the pack proves two more things for every read: no analyst could reach the layers that hold them, and every sensitive attribute an analyst did read was masked at that moment. The platform can add evidence but cannot change or delete it.")

# ---------- 12 decisions ----------
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
heading(s, "The decision log in five principles", dark=True)
rows = [("Decision", "Principle"),
        ("Identity", "The normalised application number is the only key that crosses services. A person is a keyed hash of the national id. Service UUIDs are kept and measured, never joined on."),
        ("Joins", "As of commit time, against history, to one common cut-off. Orphans are kept, out of the denominator, and published to the team that wrote them. Every entity declares its grain and a test checks it."),
        ("Governance", "Direct identifiers never enter analyst-readable schemas. Every access is logged to a store the platform cannot alter. Regulatory retention overrides erasure."),
        ("Rejected", "Holding back rows until the sources agree. It ties every metric to the worst integration and changes the denominator. Instead: one owner per fact, every disagreement published with an owner, gated in aggregate."),
        ("To confirm", "Whether the decision service can emit an inputs snapshot keyed on application number and decision version. It lifts every Q2 answer to the top evidence grade.")]
tbl = s.shapes.add_table(len(rows), 2, px(128), px(250), px(1664), px(660)).table
tbl.columns[0].width = px(430); tbl.columns[1].width = px(1234)
tbl.rows[0].height = px(70)
for i in range(1, len(rows)): tbl.rows[i].height = px(112)
for i, row in enumerate(rows):
    for j, val in enumerate(row):
        c = tbl.cell(i, j); c.text = ""
        c.fill.solid(); c.fill.fore_color.rgb = DK2 if i == 0 else (NAVY if i % 2 else DK3)
        c.margin_left = c.margin_right = px(24); c.margin_top = c.margin_bottom = px(14)
        p = c.text_frame.paragraphs[0]; r = p.add_run(); r.text = val
        r.font.name = TEXT; r.font.size = pt(26); r.font.bold = (i == 0 or j == 0)
        r.font.color.rgb = ORANGE if i == 0 else OFF
footer(s, 12, dark=True)
notes(s, "Sixty seconds, one sentence per row. On the rejected trade-off, give the reason in full: it looks safe, but holding rows ties every metric to the worst integration, and it changes the denominator so the funnel stops reconciling to application counts. The runner-up confirm item is who mints customer_id, which branch applicants carry in the KYC and disbursement services but not in the application service. On identity, the risk I wrote down: the key assumes national_id holds one ID scheme, and the platform publishes two counts, ids collapsing into one key and same name-and-mobile under different keys, so the size of the problem is visible before anyone widens the use of personal data.")

# ---------- 13 close ----------
s = prs.slides.add_slide(BLANK); bg(s, OFF)
heading(s, "Nothing open is blocking")
x0 = 128
for t, items in [("Ask the source owners", ["Six criteria the existing Kafka CDC topics must meet to replace DMS", "Which ID scheme national_id holds", "What OFFER_RETRACTED means, and whether CONTRACT_SIGNED mirrors acceptance"]),
                 ("Measure from the data", ["Whether a soft-deleted offer is re-issued on the same row", "Whether decided_at is write time or commit time", "How often ids collapse into one person key"]),
                 ("Set by their owners", ["Product: the bucket mapping and the hold threshold", "Lending squad: the flag threshold", "The data protection officer: the PII classification"])]:
    rect(s, x0, 290, 533, 380, WHITE, LINE)
    text(s, t, x0 + 32, 316, 470, 40, 28, color=ORANGE, bold=True)
    para_box(s, items, x0 + 32, 370, 470, 290, 24, gap=12, bullets=True)
    x0 += 565
text(s, "If the Kafka topics meet the six criteria, Bronze reads the topics, S3 stays the archive, and nothing downstream of Bronze changes.",
     128, 740, 1664, 120, 32, color=NAVY, font=HEAD, line=1.3)
footer(s, 13)
notes(s, "Close with the frame again: append-only, as-of, honest. Then the day-one answer if asked what you would do first: get the six Kafka answers and the national_id answer, and confirm with each owner the parameters the document leaves to them. Stop talking and invite questions.")

prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")
