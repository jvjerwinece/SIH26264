"""Build the SIH 2026 official-format deck for Ekasutra (PS 26264).

Starts from the official template each run so the result is reproducible.
Canvas is 1280x720 px; the template's own 1 px = 9525 EMU.

Usage:  python tools/build_official_deck.py [path/to/SIH2026-IDEA-Presentation-Format.pptx]
Then:   powershell -NoProfile -ExecutionPolicy Bypass -File tools/pptx2pdf.ps1 `
          -In submission/Ekasutra_SIH2026_SIH26264_Official.pptx `
          -Out submission/Ekasutra_SIH2026_SIH26264_Official.pdf
"""
import copy
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "tools" / "SIH2026-IDEA-Presentation-Format.pptx"
OUT = REPO / "submission" / "Ekasutra_SIH2026_SIH26264_Official.pptx"

EMU = 9525
INK = RGBColor.from_string("1F2A44")
MUTED = RGBColor.from_string("5A6478")
BLUE = RGBColor.from_string("0070C0")
DEEP = RGBColor.from_string("1F497D")
LIGHT = RGBColor.from_string("EAF2FA")
LINE = RGBColor.from_string("C9D8E8")
GREEN = RGBColor.from_string("1E8E5A")
AMBER = RGBColor.from_string("B26A00")
AMBER_BG = RGBColor.from_string("FFF4E0")
WHITE = RGBColor.from_string("FFFFFF")
PURPLE = RGBColor.from_string("4B2E83")
GREY_BG = RGBColor.from_string("F4F6F9")

BODY = "Arial"
HEAD = "Times New Roman"


def px(v):
    return Emu(int(round(v * EMU)))


def style_run(run, size, color=INK, bold=False, italic=False, font=BODY):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def textbox(slide, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP, margins=(0, 0, 0, 0)):
    box = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left, tf.margin_right, tf.margin_top, tf.margin_bottom = [px(m) for m in margins]
    fill_paras(tf, paras)
    return box


def fill_paras(tf, paras):
    tf.clear()
    for i, spec in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = spec.get("align", PP_ALIGN.LEFT)
        p.line_spacing = spec.get("line", 1.0)
        if "before" in spec:
            p.space_before = Pt(spec["before"])
        if "after" in spec:
            p.space_after = Pt(spec["after"])
        for text, size, opts in spec["runs"]:
            r = p.add_run()
            r.text = text
            style_run(
                r,
                size,
                color=opts.get("color", INK),
                bold=opts.get("bold", False),
                italic=opts.get("italic", False),
                font=opts.get("font", BODY),
            )


def shape(slide, kind, x, y, w, h, fill=None, line=None, line_w=1.0, adj=None):
    sh = slide.shapes.add_shape(kind, px(x), px(y), px(w), px(h))
    sh.shadow.inherit = False
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    if adj is not None:
        for i, v in enumerate(adj):
            sh.adjustments[i] = v
    sh.text_frame.word_wrap = True
    return sh


def card(slide, x, y, w, h, paras, fill=LIGHT, line=LINE, adj=(0.10,), margins=(10, 10, 6, 6), anchor=MSO_ANCHOR.TOP):
    sh = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, line=line, adj=adj)
    tf = sh.text_frame
    tf.margin_left, tf.margin_right, tf.margin_top, tf.margin_bottom = [px(m) for m in margins]
    tf.vertical_anchor = anchor
    fill_paras(tf, paras)
    return sh


def set_title(slide, text, size=34, color=DEEP):
    for sh in slide.shapes:
        if sh.name.startswith("Title"):
            sh.left, sh.top, sh.width, sh.height = px(40), px(52), px(1200), px(70)
            tf = sh.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            fill_paras(
                tf,
                [{"runs": [(text, size, {"bold": True, "font": HEAD, "color": color})], "align": PP_ALIGN.CENTER}],
            )
            return


def footer(slide):
    for sh in slide.shapes:
        if sh.name.startswith("Footer"):
            fill_paras(
                sh.text_frame,
                [{"runs": [("@Team Ekasutra  ·  SIH26264", 11, {"color": WHITE})], "align": PP_ALIGN.CENTER}],
            )
        elif sh.name.startswith("Oval"):
            sh.left, sh.top, sh.width, sh.height = px(28), px(26), px(200), px(72)
            tf = sh.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = px(2)
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            fill_paras(
                tf,
                [{"runs": [("Team Ekasutra", 13, {"bold": True, "color": PURPLE})], "align": PP_ALIGN.CENTER}],
            )


def drop(slide, prefix):
    for sh in list(slide.shapes):
        if sh.name.startswith(prefix):
            sh._element.getparent().remove(sh._element)


def kicker(slide, x, y, w, text):
    textbox(
        slide, x, y, w, 18,
        [{"runs": [(text.upper(), 10.5, {"bold": True, "color": BLUE})]}],
    )


def build():
    prs = Presentation(str(TEMPLATE))
    slides = list(prs.slides)

    # ---------- Slide 0: title ----------
    s = slides[0]
    for sh in s.shapes:
        if sh.name.startswith("Subtitle"):
            sh.left, sh.top, sh.width, sh.height = px(80), px(118), px(500), px(64)
            tf = sh.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.TOP
            tf.margin_top = tf.margin_bottom = px(0)
            fill_paras(tf, [
                {"runs": [("Ekasutra", 46, {"bold": True, "font": HEAD, "color": DEEP})]},
            ])
        if sh.name.startswith("TextBox") and sh.shape_id == 10:
            sh.left, sh.top, sh.width, sh.height = px(38), px(268), px(548), px(420)
            tf = sh.text_frame
            tf.word_wrap = True
            tf.margin_top = px(0)
            tf.margin_left = tf.margin_right = px(0)
            fill_paras(tf, [
                {"runs": [("Problem Statement ID – ", 16, {"bold": True}), ("26264", 16, {})], "after": 7},
                {"runs": [("Problem Statement Title – ", 16, {"bold": True}),
                          ("Integrated dashboard for monitoring and tracking institution-related complaint cases across AICTE Bureaus/Cells", 16, {})], "after": 7},
                {"runs": [("Theme – ", 16, {"bold": True}), ("Smart Automation", 16, {})], "after": 7},
                {"runs": [("PS Category – ", 16, {"bold": True}), ("Software", 16, {})], "after": 7},
                {"runs": [("Team ID – ", 16, {"bold": True}),
                          ("[ add from SIH portal ]", 16, {"bold": True, "color": AMBER})], "after": 7},
                {"runs": [("Team Name – ", 16, {"bold": True}), ("Team Ekasutra", 16, {})], "after": 12},
                {"runs": [("Working prototype · 90-second guided tour · synthetic case data", 11, {"color": MUTED})]},
            ])
    textbox(s, 82, 196, 500, 56, [
        {"runs": [("One institution. One thread.", 16, {"italic": True, "color": MUTED})]},
        {"runs": [("No case falls between bureaus.", 16, {"italic": True, "color": MUTED})]},
    ])

    # ---------- Slide 1: idea title / proposed solution ----------
    s = slides[1]
    set_title(s, "Ekasutra — one institution, one thread", 33)
    footer(s)
    drop(s, "TextBox")

    kicker(s, 48, 140, 500, "Proposed solution")
    textbox(s, 48, 162, 660, 40, [
        {"runs": [("AICTE hears about one institution through several offices. Ekasutra keys every complaint to its "
                   "Permanent ID so RB, PGRC and the regions share one case thread.", 13, {})], "line": 1.06},
    ])
    card(s, 48, 208, 660, 48, [
        {"runs": [("IN THE SHIPPED SEED   ", 9.5, {"bold": True, "color": AMBER}),
                  ("Sri Venkateswara College of Engineering, Kanchipuram: three fee, scholarship and intake "
                   "complaints under three name spellings — two in PGRC, one in RB.", 10.5, {})], "line": 1.04},
    ], fill=AMBER_BG, line=RGBColor.from_string("E8C9A0"), margins=(10, 10, 6, 5), anchor=MSO_ANCHOR.MIDDLE)

    blocks = [
        ("WHAT IT IS",
         "A single register of institution cases shared by the Regulation Bureau, PGRC and regional offices. "
         "Each case carries its bureau, officer, custody, status and next action."),
        ("HOW IT SOLVES THE PROBLEM",
         "Intake checks for an existing case before creating one. The overlap radar shows where RB and PGRC are "
         "acting on the same institution. One coordination room holds the joint decision, the custody chain and the SLA."),
        ("WHAT IS NEW",
         "Explainable, human-confirmed matching with zero silent merges, plus a tamper-evident audit chain. "
         "The prototype runs offline as one HTML file."),
    ]
    y = 270
    for head, body in blocks:
        textbox(s, 48, y, 660, 18, [{"runs": [(head, 11, {"bold": True, "color": BLUE})]}])
        textbox(s, 48, y + 20, 660, 60, [{"runs": [(body, 12, {})], "line": 1.06}])
        y += 100

    flow = [
        ("01", "Complaint arrives", "Email · CPGRAMS export · portal webhook"),
        ("02", "Resolve to the Permanent ID", "9,558-ID AICTE master + alias graph"),
        ("03", "One thread across bureaus", "RB · PGRC · regional office — one custody chain, one SLA"),
    ]
    x, w = 735, 495
    top = 150
    for i, (num, title, sub) in enumerate(flow):
        card(s, x, top, w, 92, [
            {"runs": [(num + "   ", 15, {"bold": True, "color": BLUE}), (title, 14.5, {"bold": True})], "after": 3},
            {"runs": [(sub, 10.5, {"color": MUTED})]},
        ], fill=LIGHT, line=LINE, margins=(14, 12, 10, 8))
        if i < 2:
            shape(s, MSO_SHAPE.DOWN_ARROW, x + w / 2 - 12, top + 100, 24, 32, fill=LINE)
        top += 140

    card(s, 48, 606, 1182, 44, [
        {"runs": [("Prevent duplicates at intake   ·   Detect RB/PGRC overlap   ·   Coordinate custody, SLA and disposal",
                   12, {"bold": True, "color": DEEP})], "align": PP_ALIGN.CENTER},
    ], fill=GREY_BG, line=None, margins=(10, 6, 8, 6), anchor=MSO_ANCHOR.MIDDLE)
    s.notes_slide.notes_text_frame.text = (
        "Ekasutra is one register keyed on the AICTE Permanent ID. The complaint is resolved to the institution once, "
        "then RB, PGRC and the regional office all work on the same thread. Nothing links automatically."
    )

    # ---------- Slide 2: technical approach ----------
    s = slides[2]
    set_title(s, "TECHNICAL APPROACH", 34)
    footer(s)
    drop(s, "TextBox")

    kicker(s, 48, 138, 400, "Stack — running today")
    now_rows = [
        ("Prototype", "one HTML file · vanilla JS · no build step · opens from file://"),
        ("Ledger", "SHA-256 chain on Web Crypto · append-only · tamper check verified"),
        ("Data pack", "PostgreSQL 16 schema · 11 tables · 18-row seed loads in psql"),
    ]
    y = 160
    for label, val in now_rows:
        textbox(s, 48, y, 96, 20, [{"runs": [(label, 10.5, {"bold": True, "color": GREEN})]}])
        textbox(s, 146, y, 486, 26, [{"runs": [(val, 11, {})], "line": 1.0}])
        y += 30

    kicker(s, 48, 258, 400, "Stack — to build before pilot")
    to_rows = [
        ("Frontend", "Next.js + TypeScript, replacing the single-file prototype"),
        ("API", "Python FastAPI over the same schema and audit function"),
        ("Matching", "pg_trgm + TF-IDF at 9,558-ID scale · browser trigram today"),
        ("Deploy", "Docker Compose · role-based access — not built yet"),
    ]
    y = 280
    for label, val in to_rows:
        textbox(s, 48, y, 96, 20, [{"runs": [(label, 10.5, {"bold": True, "color": BLUE})]}])
        textbox(s, 146, y, 486, 26, [{"runs": [(val, 11, {})], "line": 1.0}])
        y += 28

    card(s, 48, 396, 584, 82, [
        {"runs": [("HUMAN IN THE LOOP", 10.5, {"bold": True, "color": AMBER})], "after": 4},
        {"runs": [("Auto-link only when confidence and margin clear the threshold. Everything else goes to an officer "
                   "as a top-3 with evidence. No silent merges.", 11.5, {})], "line": 1.05},
    ], fill=AMBER_BG, line=RGBColor.from_string("E8C9A0"), margins=(12, 12, 9, 7))

    textbox(s, 48, 488, 584, 40, [
        {"runs": [("Each action appends:  sha256(prev || time || actor || action || object)", 10,
                   {"font": "Courier New", "color": MUTED})], "line": 1.05},
        {"runs": [("Nothing is updated in place; a chain check recomputes and compares.", 10, {"color": MUTED})]},
    ])

    stages = [
        ("01", "INGEST", "email · CPGRAMS · webhook"),
        ("02", "RESOLVE & MATCH", "master + alias + tf-idf"),
        ("03", "CASE LEDGER", "append-only events"),
        ("04", "OVERLAP ENGINE", "RB × PGRC, explainable"),
        ("05", "COORDINATE", "room, custody, SLA"),
        ("06", "DASHBOARD", "8 KPIs, reports, CSV"),
    ]
    bw, bh = 180, 70
    xs = [652, 848, 1044]
    y1, y2 = 206, 380
    for idx, (num, name, sub) in enumerate(stages):
        row, col = (0, idx) if idx < 3 else (1, 5 - idx)
        x = xs[col]
        y = y1 if row == 0 else y2
        card(s, x, y, bw, bh, [
            {"runs": [(num + "  ", 10.5, {"bold": True, "color": BLUE}), (name, 10, {"bold": True})], "after": 2},
            {"runs": [(sub, 8.5, {"color": MUTED})]},
        ], fill=LIGHT, line=LINE, margins=(8, 8, 6, 4))
    for x in (834, 1030):
        shape(s, MSO_SHAPE.RIGHT_ARROW, x, y1 + 21, 12, 28, fill=LINE)
        shape(s, MSO_SHAPE.LEFT_ARROW, x, y2 + 21, 12, 28, fill=LINE)
    shape(s, MSO_SHAPE.DOWN_ARROW, 1128, y1 + bh + 4, 12, y2 - (y1 + bh) - 8, fill=LINE)

    textbox(s, 652, 470, 572, 30, [
        {"runs": [("Prototype covers stages 01–06 with seeded data; the API and PostgreSQL schema are specified in the repo.",
                   10, {"color": MUTED})], "line": 1.05},
    ])
    card(s, 48, 566, 1182, 44, [
        {"runs": [("Opens from file:// — no host, no login, no cold start  ·  9 views, 0 console errors  ·  "
                   "rules decide, a statistical text check assists", 12, {"bold": True, "color": DEEP})],
         "align": PP_ALIGN.CENTER},
    ], fill=GREY_BG, line=None, margins=(10, 6, 8, 6), anchor=MSO_ANCHOR.MIDDLE)
    s.notes_slide.notes_text_frame.text = (
        "Rules decide, a statistical text check assists. Every match is explainable and every action is attributable. "
        "Auto-link only when confidence and margin clear the threshold; otherwise a person confirms."
    )

    # ---------- Slide 3: feasibility and viability ----------
    s = slides[3]
    set_title(s, "FEASIBILITY AND VIABILITY", 34)
    footer(s)
    drop(s, "TextBox")

    kicker(s, 48, 140, 400, "Built and measured")
    metrics = [
        ("9,558", "AICTE Permanent IDs"),
        ("367", "labelled name variants"),
        ("94.6%", "top-1 match"),
        ("99.7%", "top-3 recall"),
        ("0", "silent merges"),
    ]
    positions = [(48, 166), (232, 166), (416, 166), (48, 262), (232, 262)]
    for (value, label), (x, y) in zip(metrics, positions):
        card(s, x, y, 176, 80, [
            {"runs": [(value, 22, {"bold": True, "color": DEEP})], "after": 1},
            {"runs": [(label, 9, {"color": MUTED})]},
        ], fill=WHITE, line=LINE, margins=(10, 10, 6, 5), anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 48, 352, 600, 32, [
        {"runs": [("367 is the evaluation set; 9,558 is the size of the AICTE master, not the test set. "
                   "Ambiguous names route to a person.", 9.5, {"color": MUTED, "italic": True})], "line": 1.05},
    ])

    feas = [
        ("TECHNICAL", "working HTML prototype; resolver benchmarked on 367 variants; audit chain verified end to end."),
        ("OPERATIONAL", "keeps existing email and CPGRAMS intake; institutions do not learn a new portal."),
        ("ECONOMIC", "one API and one database; no new hardware, no licensed matching product."),
    ]
    y = 398
    for label, text in feas:
        textbox(s, 48, y, 96, 18, [{"runs": [(label, 9.5, {"bold": True, "color": BLUE})]}])
        textbox(s, 146, y, 440, 34, [{"runs": [(text, 10.5, {})], "line": 1.0}])
        y += 40

    kicker(s, 720, 140, 400, "What can break → what we do")
    risks = [
        ("What if the matcher picks the wrong institution?",
         "Nothing merges on a score. A top-3 with the evidence goes to an officer; 0 auto-merges across 367 variants."),
        ("What if the institution master is not ours to ship?",
         "It is public AICTE data, so the pack ships the schema and the 367 variants we built, not the list."),
        ("What if bureaus keep working the old way?",
         "Email and CPGRAMS intake stay; nobody is asked to learn a new portal before the register earns it."),
        ("What if two audit writes land at once?",
         "Known gap — the chain can fork. An advisory lock plus a unique index on prev_hash is scheduled, not done."),
        ("What if the jury asks about security?",
         "Role-based access is not built. The demo role switch is a view, not access control."),
    ]
    y = 164
    for head, body in risks:
        card(s, 720, y, 510, 64, [
            {"runs": [(head, 11, {"bold": True})], "after": 3},
            {"runs": [(body, 10, {"color": MUTED})], "line": 1.02},
        ], fill=LIGHT, line=LINE, margins=(12, 12, 7, 5))
        y += 74

    card(s, 48, 540, 1182, 62, [
        {"runs": [("SIX-WEEK PILOT   ", 10.5, {"bold": True, "color": BLUE}),
                  ("W1–2 connect intake + master  ·  W3–4 RB, PGRC and one regional office live  ·  "
                   "W5 harden roles and audit lock  ·  W6 rehearse and hand over", 11, {})], "line": 1.05},
    ], fill=GREY_BG, line=None, margins=(12, 10, 8, 8), anchor=MSO_ANCHOR.MIDDLE)
    s.notes_slide.notes_text_frame.text = (
        "Feasibility is measured, not asserted: 367 labelled variants, 94.6 percent top-1, 99.7 percent top-3, "
        "zero silent merges. The audit concurrency gap is known and scheduled before any pilot."
    )

    # ---------- Slide 4: impact and benefits ----------
    s = slides[4]
    set_title(s, "IMPACT AND BENEFITS", 34)
    footer(s)
    drop(s, "TextBox")

    cols = [
        ("OFFICERS", [
            "One register, not two",
            "Overlap visible before duplicate action",
            "Custody and SLA on one screen",
        ]),
        ("INSTITUTIONS & STUDENTS", [
            "One complaint, one case ID",
            "A transfer cannot go missing",
            "Status visible without an RTI",
        ]),
        ("AICTE SYSTEM", [
            "Institution-, region-, bureau- and status-wise reports",
            "Alerts before the timeline, not after",
            "Every action attributable in a hash chain",
        ]),
    ]
    x = 48
    for head, items in cols:
        textbox(s, x, 146, 360, 20, [{"runs": [(head, 11, {"bold": True, "color": BLUE})]}])
        y = 176
        for item in items:
            textbox(s, x, y, 350, 40, [
                {"runs": [("•  ", 13, {"color": BLUE}), (item, 12, {})], "line": 1.02},
            ])
            y += 54
        x += 402

    stats = [
        ("~100–200", "officer-days a year",
         "Modelled at 1,000 cases, 5–10% overlap and 2 officer-days per duplicate."),
        ("7 → 3", "cases collapse to threads",
         "In the shipped 32-case seed, 7 complaints about 3 institutions sit split across RB and PGRC under "
         "different name spellings. All 3 overlaps span both bureaus."),
        ("0", "silent merges",
         "Ambiguous matches go to a person, never into the register automatically."),
    ]
    x = 48
    for big, small, note in stats:
        card(s, x, 380, 380, 130, [
            {"runs": [(big, 26, {"bold": True, "color": DEEP})], "after": 0},
            {"runs": [(small, 11, {"bold": True, "color": BLUE})], "after": 5},
            {"runs": [(note, 9.5, {"color": MUTED})], "line": 1.03},
        ], fill=LIGHT, line=LINE, margins=(14, 12, 8, 8))
        x += 402

    textbox(s, 48, 540, 1182, 60, [
        {"runs": [("Social: a student sees one case ID and one owner.   Economic: officer time moves from de-duplication to disposal.   "
                   "Governance: every transfer and decision is attributable.", 11.5, {})], "line": 1.08},
        {"runs": [("Built for AICTE. The same pattern fits any regulator with several cells and one institution master.",
                   10, {"color": MUTED, "italic": True})], "before": 4},
    ])
    card(s, 48, 612, 1182, 42, [
        {"runs": [("PS 26264 — all eight objectives are demoable in the prototype today", 12,
                   {"bold": True, "color": DEEP})], "align": PP_ALIGN.CENTER},
    ], fill=GREY_BG, line=None, margins=(10, 6, 8, 6), anchor=MSO_ANCHOR.MIDDLE)
    s.notes_slide.notes_text_frame.text = (
        "Impact is stated with its assumption. The officer-day figure is a model at 1,000 cases a year, not a measurement. "
        "The defensible claims are the benchmark, the audit chain and the single case thread."
    )

    # ---------- Slide 5: research and references ----------
    s = slides[5]
    set_title(s, "RESEARCH  AND REFERENCES", 34)
    footer(s)
    drop(s, "TextBox")

    kicker(s, 48, 140, 400, "Sources")
    refs = [
        ("SIH 2026 — Problem Statement 26264", "Smart India Hackathon portal", "sih.gov.in"),
        ("AICTE Approval Process Handbook 2026–27", "All India Council for Technical Education", "aicte-india.org"),
        ("UGC (Redress of Grievances) Regulations, 2019", "University Grants Commission", "ugc.gov.in"),
        ("Salton & Buckley (1988), Term-weighting approaches in automatic text retrieval",
         "Information Processing & Management 24(5), 513–523", "doi.org/10.1016/0306-4573(88)90021-0"),
        ("NIST FIPS 180-4 (2015), Secure Hash Standard", "National Institute of Standards and Technology",
         "csrc.nist.gov/pubs/fips/180-4/upd1/final"),
        ("Public intake channels the register reads from", "AICTE institution listings · CPGRAMS grievances",
         "aicte-india.org · cpgrams.gov.in"),
    ]
    y = 168
    for i, (title, source, link) in enumerate(refs, 1):
        textbox(s, 48, y, 660, 52, [
            {"runs": [(f"{i}.  ", 11, {"bold": True, "color": BLUE}), (title, 11, {"bold": True})], "line": 1.02},
            {"runs": [(source + "  ·  ", 9.5, {"color": MUTED}), (link, 9.5, {"color": BLUE})]},
        ])
        y += 58

    card(s, 752, 158, 478, 260, [
        {"runs": [("PROTOTYPE & EVIDENCE", 11, {"bold": True, "color": BLUE})], "after": 8},
        {"runs": [("One offline HTML file with a 90-second guided tour", 10.5, {})], "after": 5},
        {"runs": [("9 views navigate with 0 console errors", 10.5, {})], "after": 5},
        {"runs": [("18-row seed · chain head verified · row tamper detected", 10.5, {})], "after": 5},
        {"runs": [("367 labelled variants · 94.6% top-1 · 99.7% top-3", 10.5, {})], "after": 5},
        {"runs": [("Case data is synthetic; no real complainant data is used", 10.5, {})], "after": 8},
        {"runs": [("DATA ACCESS   ", 9.5, {"bold": True, "color": AMBER}),
                  ("the institution master is public AICTE data and is not redistributed in this pack; "
                   "the 367-variant test set is ours and ships with the repo.", 9.5, {"color": MUTED})], "line": 1.05},
    ], fill=LIGHT, line=LINE, margins=(16, 14, 10, 8))

    textbox(s, 48, 528, 660, 40, [
        {"runs": [("The matching benchmark and the audit chain are our own tests; the references above are external "
                   "sources, not validation of our results.", 9.5, {"italic": True, "color": MUTED})], "line": 1.05},
    ])
    card(s, 48, 612, 1182, 42, [
        {"runs": [("No hosted demo to time out — the prototype is one offline HTML file, opened live during the jury round.",
                   12, {"bold": True, "color": DEEP})], "align": PP_ALIGN.CENTER},
    ], fill=GREY_BG, line=None, margins=(10, 6, 8, 6), anchor=MSO_ANCHOR.MIDDLE)
    s.notes_slide.notes_text_frame.text = (
        "Six sources: the problem statement, AICTE's approval handbook, the UGC grievance regulations, "
        "the TF-IDF weighting paper, FIPS 180-4, and the public intake channels the register reads from. "
        "Our own benchmark is separate from these references, and the data-access line says what we do and do not ship."
    )

    # ---------- drop the instructions slide ----------
    sld_ids = prs.slides._sldIdLst
    sld_ids.remove(list(sld_ids)[6])

    prs.save(str(OUT))
    print("saved", OUT)
    print("slides", len(prs.slides))


if __name__ == "__main__":
    build()
