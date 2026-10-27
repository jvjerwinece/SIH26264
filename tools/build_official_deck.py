"""Build the SIH 2026 official-format deck for Ekasutra (PS 26264).

Starts from the official template each run so the result is reproducible.
Canvas is 1280x720 px; the template's own 1 px = 9525 EMU.

Usage:  python tools/build_official_deck.py [path/to/SIH2026-IDEA-Presentation-Format.pptx]
Then:   powershell -NoProfile -ExecutionPolicy Bypass -File tools/pptx2pdf.ps1 `
          -In submission/Ekasutra_SIH2026_SIH26264_Official.pptx `
          -Out submission/Ekasutra_SIH2026_SIH26264_Official.pdf
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "tools" / "SIH2026-IDEA-Presentation-Format.pptx"
OUT = REPO / "submission" / "Ekasutra_SIH2026_SIH26264_Official.pptx"
MEDIA = REPO / "submission" / "media"

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
GREEN_BG = RGBColor.from_string("E7F4EE")

BODY = "Arial"
HEAD = "Times New Roman"
ICON = "Segoe MDL2 Assets"


def px(v):
    return Emu(int(round(v * EMU)))


def style_run(run, size, color=INK, bold=False, italic=False, font=BODY, spc=None):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    if spc is not None:
        run.font._element.set("spc", str(int(spc)))


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
                spc=opts.get("spc"),
            )


def textbox(slide, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP, margins=(0, 0, 0, 0)):
    box = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left, tf.margin_right, tf.margin_top, tf.margin_bottom = [px(m) for m in margins]
    fill_paras(tf, paras)
    return box


def shape(slide, kind, x, y, w, h, fill=None, line=None, line_w=1.0, adj=None, dash=False):
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
        if dash:
            sh.line.dash_style = MSO_LINE.DASH
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


def picture(slide, path, x, y, w, h, border=LINE):
    pic = slide.shapes.add_picture(str(path), px(x), px(y), px(w), px(h))
    if border is not None:
        pic.line.color.rgb = border
        pic.line.width = Pt(1.0)
    return pic


def set_title(slide, text, size=38, color=DEEP):
    for sh in slide.shapes:
        if sh.name.startswith("Title"):
            sh.left, sh.top, sh.width, sh.height = px(40), px(46), px(1200), px(62)
            tf = sh.text_frame
            tf.word_wrap = True
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            fill_paras(
                tf,
                [{"runs": [(text, size, {"bold": True, "font": HEAD, "color": color, "spc": 20})],
                  "align": PP_ALIGN.CENTER}],
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
            sh.left, sh.top, sh.width, sh.height = px(30), px(24), px(165), px(62)
            tf = sh.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = px(2)
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            fill_paras(
                tf,
                [{"runs": [("Team Ekasutra", 12.5, {"bold": True, "color": PURPLE})], "align": PP_ALIGN.CENTER}],
            )


def drop(slide, prefix):
    for sh in list(slide.shapes):
        if sh.name.startswith(prefix):
            sh._element.getparent().remove(sh._element)


def section(slide, x, y, w, text, color=BLUE):
    textbox(slide, x, y, w, 20,
            [{"runs": [(text.upper(), 12.5, {"bold": True, "color": color, "spc": 90})]}])


def chip(slide, x, y, w, h, text, fg=INK, bg=WHITE, border=LINE, size=11.5, bold=True):
    card(slide, x, y, w, h, [{"runs": [(text, size, {"bold": bold, "color": fg})], "align": PP_ALIGN.CENTER}],
         fill=bg, line=border, adj=(0.35,), margins=(6, 6, 2, 2), anchor=MSO_ANCHOR.MIDDLE)


def disc(slide, x, y, d, fill, glyph, size, color):
    sh = shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill=fill, line=None)
    tf = sh.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = glyph
    style_run(r, size, color=color, font=ICON)
    return sh


def down_arrow(slide, cx, y, h, color=LINE, w=16):
    shape(slide, MSO_SHAPE.DOWN_ARROW, cx - w / 2, y, w, h, fill=color)


def right_arrow(slide, x, cy, w, color=LINE, h=18):
    shape(slide, MSO_SHAPE.RIGHT_ARROW, x, cy - h / 2, w, h, fill=color)


def connector(slide, x1, y1, x2, y2, color=LINE, width=1.6):
    c = slide.shapes.add_connector(1, px(x1), px(y1), px(x2), px(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    return c


def elbow(slide, x1, y1, x2, y2, color=LINE, width=1.6):
    mid = (y1 + y2) / 2
    connector(slide, x1, y1, x1, mid, color, width)
    connector(slide, x1, mid, x2, mid, color, width)
    connector(slide, x2, mid, x2, y2, color, width)


def build():
    prs = Presentation(str(TEMPLATE))
    slides = list(prs.slides)

    # ---------- Slide 0: title (template layout, values filled) ----------
    s = slides[0]
    for sh in s.shapes:
        if sh.name.startswith("Subtitle"):
            fill_paras(sh.text_frame, [])
        if sh.name.startswith("TextBox") and sh.shape_id == 10:
            sh.left, sh.top, sh.width, sh.height = px(38), px(186), px(610), px(300)
            tf = sh.text_frame
            tf.word_wrap = True
            tf.margin_top = px(0)
            tf.margin_left = tf.margin_right = px(0)
            v, b = 16.5, {"bold": True}
            fill_paras(tf, [
                {"runs": [("•  Problem Statement ID : ", v, b), ("26264", v, {**b, "color": GREEN})], "after": 12},
                {"runs": [("•  Problem Statement Title : ", v, b),
                          ("Integrated dashboard for monitoring and tracking institution-related complaint cases "
                           "across AICTE Bureaus/Cells", v, {**b, "color": GREEN})], "after": 12},
                {"runs": [("•  Theme : ", v, b), ("Smart Automation", v, {**b, "color": GREEN})], "after": 12},
                {"runs": [("•  PS Category : ", v, b), ("Software", v, {**b, "color": GREEN})], "after": 12},
                {"runs": [("•  Team ID : ", v, b), ("[ add from SIH portal ]", v, {"bold": True, "color": AMBER})],
                 "after": 12},
                {"runs": [("•  Team Name : ", v, b), ("Team Ekasutra", v, {**b, "color": GREEN})]},
            ])
    shape(s, MSO_SHAPE.RECTANGLE, 38, 506, 64, 3, fill=BLUE)
    textbox(s, 38, 520, 560, 64, [
        {"runs": [("One complaint register, keyed on the AICTE Permanent ID, shared by every bureau "
                   "that touches the case.", 15, {"italic": True, "color": DEEP})], "line": 1.14},
    ])

    # ---------- Slide 1: idea title / proposed solution ----------
    s = slides[1]
    set_title(s, "One institution, one thread", 38)
    footer(s)
    drop(s, "TextBox")

    LX, LW = 48, 640
    blocks = [
        (128, "The problem today",
         "A complaint about one college can arrive at RB, PGRC or a regional office. "
         "Each office types the name its own way, so one institution becomes three records that never meet."),
        (256, "What Ekasutra does",
         "Every complaint is resolved once to the AICTE Permanent ID. From that point the case thread "
         "is shared: one owner at a time, one history, and one place where any bureau can look before "
         "it acts."),
        (384, "What is new",
         "Matching is rules-first and it shows its reasons. An officer confirms before two cases are "
         "linked, and that decision is written to a hash-chained audit trail."),
    ]
    for y, head, body in blocks:
        section(s, LX, y, LW, head)
        textbox(s, LX, y + 22, LW, 96, [{"runs": [(body, 15, {})], "line": 1.12}])

    card(s, LX, 514, LW, 104, [
        {"runs": [("IN THE SHIPPED SEED", 11, {"bold": True, "color": AMBER, "spc": 90})], "after": 4},
        {"runs": [("Three cases about Vidyasagara College of Engineering arrived under different spellings. "
                   "Two sat with PGRC and one with RB, and the register keeps all three on one thread for a "
                   "single officer to review.", 12.5, {})], "line": 1.1},
    ], fill=AMBER_BG, line=RGBColor.from_string("E8C9A0"), margins=(14, 14, 9, 8))

    textbox(s, LX, 626, LW, 30, [
        {"runs": [("Open the prototype file and this exact case is on the dashboard. Synthetic data throughout.",
                   11.5, {"color": MUTED})], "line": 1.15},
    ])

    RX, RW = 726, 506
    picture(s, MEDIA / "dash_main.png", RX, 130, RW, 316)
    textbox(s, RX, 452, RW, 18, [
        {"runs": [("Dashboard, the live prototype opened from a single file", 11, {"color": MUTED})]},
    ])

    steps = [("01", "Resolve the institution"), ("02", "Review the overlap"), ("03", "Share the thread")]
    sx = RX
    for num, label in steps:
        card(s, sx, 480, 162, 66, [
            {"runs": [(num + "   ", 13, {"bold": True, "color": BLUE}), (label, 11.5, {"bold": True})], "line": 1.05},
        ], fill=LIGHT, line=LINE, margins=(10, 10, 6, 6), anchor=MSO_ANCHOR.MIDDLE)
        sx += 172

    textbox(s, RX, 562, RW, 56, [
        {"runs": [("“I can see the other bureau’s case before I decide.”", 14, {"italic": True, "color": DEEP})],
         "line": 1.1},
        {"runs": [("That is the whole product in one sentence.", 11.5, {"color": MUTED})]},
    ])
    s.notes_slide.notes_text_frame.text = (
        "Ekasutra is one register keyed on the AICTE Permanent ID. The complaint is resolved to the institution once, "
        "then RB, PGRC and the regional office all work on the same thread. Nothing links automatically."
    )

    # ---------- Slide 2: technical approach — decision tree ----------
    s = slides[2]
    set_title(s, "TECHNICAL APPROACH", 38)
    footer(s)
    drop(s, "TextBox")

    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 48, 140, 196, 46, fill=WHITE, line=LINE, adj=(0.35,))
    disc(s, 56, 150, 26, AMBER_BG, "\uE7BA", 13, AMBER)
    textbox(s, 88, 140, 148, 46, [
        {"runs": [("Complaint arrives", 12, {"bold": True, "color": INK})]}], anchor=MSO_ANCHOR.MIDDLE)
    right_arrow(s, 248, 163, 16, INK, h=16)

    dec = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 266, 116, 462, 92, fill=INK, line=None, adj=(0.10,))
    disc(s, 282, 145, 34, BLUE, "\uE721", 15, WHITE)
    tf = dec.text_frame
    tf.margin_left, tf.margin_right = px(46), px(8)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    fill_paras(tf, [
        {"runs": [("Do we already know this institution?", 16.5, {"bold": True, "color": WHITE})],
         "align": PP_ALIGN.CENTER, "after": 2},
        {"runs": [("checked against name, alias, city and Permanent ID", 10.5, {"color": LIGHT})],
         "align": PP_ALIGN.CENTER},
    ])

    textbox(s, 764, 124, 468, 76, [
        {"runs": [("No score ever links two cases. Every branch ends at a named officer, and the chain records "
                   "who decided.", 14, {"italic": True, "color": DEEP})], "line": 1.15},
    ])

    branches = [
        {
            "x": 48, "color": GREEN, "tint": GREEN_BG, "tag": "A", "head": "ID OR ALIAS MATCHES",
            "mark": "\uE73E",
            "nodes": [
                ("\uE8A1", "Exact Permanent ID", "or a spelling we already hold"),
                ("\uE721", "Evidence on screen", "which token matched, and where"),
                ("\uE77B", "Officer confirms", "link, relate, or keep separate"),
            ],
            "out": "The case joins an existing thread.",
        },
        {
            "x": 436, "color": AMBER, "tint": AMBER_BG, "tag": "B", "head": "THE NAME IS FUZZY",
            "mark": "\uE77B",
            "nodes": [
                ("\uE71D", "Three best candidates", "ranked by rules, then text similarity"),
                ("\uE73E", "Officer picks one", "the reason for the pick is saved"),
                ("\uE8AB", "Or rejects all three", "a new case opens, untouched"),
            ],
            "out": "No merge without a named officer.",
        },
        {
            "x": 824, "color": BLUE, "tint": LIGHT, "tag": "C", "head": "NOT IN THE MASTER",
            "mark": "\uEA18",
            "nodes": [
                ("\uE8A5", "New institution record", "created with the raw name as written"),
                ("\uE8B9", "Master review queue", "queued for the data team to approve"),
                ("\uE9CE", "Provisional linking", "held until the Permanent ID is confirmed"),
            ],
            "out": "No silent identity is invented.",
        },
    ]
    for b in branches:
        x, c, tint = b["x"], b["color"], b["tint"]
        elbow(s, 497, 208, x + 186, 230, color=c, width=1.8)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 230, 372, 298, fill=tint, line=c, line_w=1.4, adj=(0.05,), dash=True)
        disc(s, x + 14, 240, 20, c, b["tag"], 10, WHITE)
        textbox(s, x + 40, 240, 318, 20, [
            {"runs": [(b["head"], 11.5, {"bold": True, "color": c, "spc": 70})]}], anchor=MSO_ANCHOR.MIDDLE)
        ny = 266
        for i, (glyph, head, sub) in enumerate(b["nodes"]):
            shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 18, ny, 336, 44, fill=WHITE, line=c, line_w=1.0, adj=(0.18,))
            disc(s, x + 26, ny + 9, 26, tint, glyph, 12.5, c)
            textbox(s, x + 60, ny + 5, 284, 15, [{"runs": [(head, 12.5, {"bold": True})]}])
            textbox(s, x + 60, ny + 24, 284, 15, [{"runs": [(sub, 10.5, {"color": MUTED})]}])
            if i < 2:
                down_arrow(s, x + 186, ny + 46, 10, c, w=14)
            ny += 56

        down_arrow(s, x + 186, 424, 14, c, w=14)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 18, 452, 336, 54, fill=WHITE, line=c, line_w=1.0, adj=(0.30,))
        disc(s, x + 26, 466, 26, c, b["mark"], 12, WHITE)
        textbox(s, x + 60, 452, 282, 54, [
            {"runs": [(b["out"], 12, {"bold": True, "color": c})], "line": 1.05}], anchor=MSO_ANCHOR.MIDDLE)

    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 48, 548, 1148, 98, fill=GREY_BG, line=LINE, adj=(0.06,))
    textbox(s, 66, 558, 150, 18, [{"runs": [("TECH STACK", 11.5, {"bold": True, "color": DEEP, "spc": 90})]}])
    textbox(s, 66, 578, 170, 16, [{"runs": [("runs today", 10, {"color": GREEN})]}])
    for i, t in enumerate(["HTML + JS", "Web Crypto", "PostgreSQL 14", "11 tables"]):
        chip(s, 66 + i * 144, 598, 134, 30, t, fg=INK, bg=WHITE, border=LINE, size=10.5)
    textbox(s, 652, 578, 190, 16, [{"runs": [("pilot build, not built yet", 10, {"color": AMBER})]}])
    for i, t in enumerate(["Next.js", "FastAPI", "pg_trgm", "Docker"]):
        chip(s, 652 + i * 132, 598, 122, 30, t, fg=MUTED, bg=WHITE, border=LINE, size=10.5)
    s.notes_slide.notes_text_frame.text = (
        "Rules decide, a statistical text check assists. Every match is explainable and every action is attributable. "
        "Auto-link only when confidence and margin clear the threshold; otherwise a person confirms."
    )

    # ---------- Slide 3: feasibility and viability ----------
    s = slides[3]
    set_title(s, "FEASIBILITY AND VIABILITY", 38)
    footer(s)
    drop(s, "TextBox")

    section(s, 48, 128, 560, "Built and measured")
    metrics = [
        ("9,558", "AICTE Permanent IDs", 48, 152),
        ("367", "name variants", 232, 152),
        ("94.6%", "top-1 match", 416, 152),
        ("99.7%", "top-3 recall", 48, 244),
        ("0", "silent merges", 232, 244),
    ]
    for value, label, x, y in metrics:
        card(s, x, y, 168, 80, [
            {"runs": [(value, 31, {"bold": True, "color": DEEP})], "after": 1},
            {"runs": [(label, 10.5, {"color": MUTED})]},
        ], fill=WHITE, line=LINE, margins=(12, 12, 6, 5), anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 416, 244, 190, 80, [
        {"runs": [("Measured on a labelled set we built and ship with the prototype.",
                   11, {"italic": True, "color": MUTED})], "line": 1.1},
    ], anchor=MSO_ANCHOR.MIDDLE)

    textbox(s, 48, 334, 580, 30, [
        {"runs": [("367 is the test set; 9,558 is the size of the AICTE master. Names we cannot separate go to a person.",
                   11.5, {"color": MUTED})], "line": 1.1},
    ])

    feas = [
        ("TECHNICAL", "The prototype and the PostgreSQL schema both run; a production API is specified, not written."),
        ("OPERATIONAL", "A pilot can keep the current email and CPGRAMS intake and add a shared register beside it."),
        ("ECONOMIC", "Every component is open source, so there is no matching licence to buy. Implementation cost is not estimated."),
    ]
    y = 378
    for label, text in feas:
        textbox(s, 48, y, 106, 18, [{"runs": [(label, 10.5, {"bold": True, "color": BLUE})]}])
        textbox(s, 160, y - 2, 468, 40, [{"runs": [(text, 13.5, {})], "line": 1.08}])
        y += 52

    section(s, 648, 128, 584, "What could break, and what we do", AMBER)
    risks = [
        ("If the name is ambiguous",
         "Rank the candidates and show the reasons. An officer decides; a score never merges two cases."),
        ("If the master cannot be shared",
         "The master is not in this pack. A pilot needs authorised access and a data-sharing agreement first."),
        ("If offices keep their old intake",
         "The register sits beside the existing routes. Nothing is switched off on day one."),
        ("If two audit writes land at once",
         "Known gap: the chain can fork. An advisory lock and a unique index on prev_hash are scheduled."),
        ("If the jury asks about security",
         "Role-based access is not built. The demo role switch is a view, not access control."),
    ]
    y = 152
    for head, body in risks:
        card(s, 648, y, 584, 78, [
            {"runs": [(head, 13, {"bold": True})], "after": 3},
            {"runs": [(body, 11.5, {"color": MUTED})], "line": 1.06},
        ], fill=LIGHT, line=LINE, margins=(14, 14, 8, 6))
        y += 86

    card(s, 48, 552, 580, 90, [
        {"runs": [("SIX-WEEK PILOT", 11, {"bold": True, "color": BLUE, "spc": 80})], "after": 3},
        {"runs": [("Two weeks to connect intake and the master, two to run a real bureau trial, one to harden roles "
                   "and the audit lock, and one to hand over.", 11.5, {})], "line": 1.06},
    ], fill=WHITE, line=LINE, margins=(14, 12, 7, 6))
    s.notes_slide.notes_text_frame.text = (
        "Feasibility is measured, not asserted: 367 labelled variants, 94.6 percent top-1, 99.7 percent top-3, "
        "zero silent merges. The audit concurrency gap is known and scheduled before any pilot."
    )

    # ---------- Slide 4: impact and benefits ----------
    s = slides[4]
    set_title(s, "IMPACT AND BENEFITS", 38)
    footer(s)
    drop(s, "TextBox")

    picture(s, MEDIA / "reports_band.png", 48, 128, 540, 288)
    textbox(s, 48, 424, 540, 18, [
        {"runs": [("Reports: filters, register, disposal rate, ageing, exported as CSV", 11, {"color": MUTED})]},
    ])

    rows = [
        ("Consolidate", "Institution profile + case register"),
        ("Identify owner", "Bureau and officer on each case"),
        ("Track movement", "Status and case-event timeline"),
        ("Detect overlap", "Radar groups same-institution cases"),
        ("Coordinate", "Room holds decision and activity"),
        ("Monitor workload", "Filters cover five case statuses"),
        ("Report", "Institution / region / bureau / status + CSV"),
        ("Watch timelines", "SLA ageing and due-case alerts"),
    ]
    shape(s, MSO_SHAPE.RECTANGLE, 620, 128, 612, 222, fill=WHITE, line=LINE)
    shape(s, MSO_SHAPE.RECTANGLE, 620, 128, 612, 30, fill=DEEP, line=None)
    textbox(s, 634, 128, 190, 30,
            [{"runs": [("WHAT THE PS ASKS", 11, {"bold": True, "color": WHITE, "spc": 70})]}],
            anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, 822, 128, 396, 30,
            [{"runs": [("WHAT THE PROTOTYPE SHOWS", 11, {"bold": True, "color": WHITE, "spc": 70})]}],
            anchor=MSO_ANCHOR.MIDDLE)
    ry = 158
    for i, (need, path) in enumerate(rows):
        if i % 2 == 1:
            shape(s, MSO_SHAPE.RECTANGLE, 621, ry, 610, 24, fill=GREY_BG, line=None)
        textbox(s, 634, ry, 182, 24, [{"runs": [(need, 11.5, {"bold": True, "color": DEEP})]}],
                anchor=MSO_ANCHOR.MIDDLE)
        textbox(s, 822, ry, 396, 24, [{"runs": [("→  " + path, 11, {})]}], anchor=MSO_ANCHOR.MIDDLE)
        ry += 24
    textbox(s, 620, 358, 612, 22, [
        {"runs": [("All eight objectives are demonstrable today. Multi-user access is not.",
                   10.5, {"italic": True, "color": MUTED})]},
    ])

    stats = [
        ("ECONOMIC", "100–200*", "officer-days a year",
         "Modelled at 1,000 cases, 5–10% overlap and two days per duplicate."),
        ("SOCIAL", "SLA", "ageing visible",
         "Overdue cases rise to the top instead of waiting for a reminder."),
        ("GOVERNANCE", "0", "silent case merges",
         "Candidate overlap is reviewed; a person decides whether to link."),
    ]
    x = 48
    for tag, big, small, note in stats:
        card(s, x, 470, 376, 104, [
            {"runs": [(tag, 9.5, {"bold": True, "color": BLUE, "spc": 70})], "after": 2},
            {"runs": [(big + "  ", 26, {"bold": True, "color": DEEP}),
                      (small, 11.5, {"bold": True, "color": BLUE})], "after": 3},
            {"runs": [(note, 10.5, {"color": MUTED})], "line": 1.06},
        ], fill=LIGHT, line=LINE, margins=(14, 12, 8, 6), anchor=MSO_ANCHOR.MIDDLE)
        x += 403

    textbox(s, 48, 588, 1182, 26, [
        {"runs": [("A student gets one case number to quote. An officer stops re-reading the same complaint. "
                   "A director can see who decided what, and when.", 14, {})], "line": 1.12},
    ])
    textbox(s, 48, 618, 1182, 40, [
        {"runs": [("*Model only, not a measurement.   ", 10.5, {"italic": True, "color": MUTED}),
                  ("ENVIRONMENTAL   ", 10.5, {"bold": True, "color": BLUE}),
                  ("the prototype ships as one HTML file and needs no server to run.", 10.5, {"color": MUTED})],
         "line": 1.1},
    ])
    s.notes_slide.notes_text_frame.text = (
        "Impact is stated with its assumption. The officer-day figure is a model at 1,000 cases a year, not a measurement. "
        "The defensible claims are the benchmark, the audit chain and the single case thread."
    )

    # ---------- Slide 5: research and references ----------
    s = slides[5]
    set_title(s, "RESEARCH AND REFERENCES", 38)
    footer(s)
    drop(s, "TextBox")

    section(s, 48, 128, 600, "Sources we relied on")
    refs = [
        ("SIH 2026 — Problem Statement 26264", "Smart India Hackathon portal", "sih.gov.in"),
        ("AICTE Approval Process Handbook 2026–27", "All India Council for Technical Education", "aicte-india.org"),
        ("UGC (Redress of Grievances) Regulations, 2019", "University Grants Commission", "ugc.gov.in"),
        ("Salton & Buckley (1988), Term-weighting approaches",
         "Information Processing & Management 24(5)", "doi.org/10.1016/0306-4573(88)90021-0"),
        ("NIST FIPS 180-4 (2015), Secure Hash Standard", "National Institute of Standards and Technology",
         "csrc.nist.gov/pubs/fips/180-4/upd1/final"),
        ("Public intake channels the register reads from", "AICTE institution listings · CPGRAMS grievances",
         "aicte-india.org · cpgrams.gov.in"),
    ]
    y = 152
    for i, (title, source, link) in enumerate(refs, 1):
        textbox(s, 48, y, 600, 50, [
            {"runs": [(f"{i}.  ", 13, {"bold": True, "color": BLUE}), (title, 13, {"bold": True})], "line": 1.04},
            {"runs": [(source + "  ·  ", 11, {"color": MUTED}), (link, 11, {"color": BLUE})]},
        ])
        y += 62

    textbox(s, 48, 522, 600, 56, [
        {"runs": [("Our benchmark and the audit-chain tests are our own work. The sources above are background; "
                   "they do not validate our results.", 11.5, {"italic": True, "color": MUTED})], "line": 1.12},
    ])

    card(s, 686, 124, 546, 424, [
        {"runs": [("PROTOTYPE & EVIDENCE", 12, {"bold": True, "color": BLUE, "spc": 80})]},
    ], fill=LIGHT, line=LINE, margins=(16, 14, 10, 8))
    picture(s, MEDIA / "radar_card.png", 702, 164, 514, 186)
    textbox(s, 702, 354, 514, 18, [
        {"runs": [("Overlap radar: 98% match, the reasons beside it, and an officer who confirms", 10, {"color": MUTED})]},
    ])
    for i, t in enumerate(["18 audit events", "SHA-256 chain intact", "0 silent merges"]):
        chip(s, 702 + i * 172, 380, 164, 30, t, fg=DEEP, bg=WHITE, border=LINE, size=10.5)

    textbox(s, 702, 420, 514, 60, [
        {"runs": [("367 labelled variants · 94.6% top-1 · 99.7% top-3", 12.5, {})], "after": 5},
        {"runs": [("9 views · 0 console errors · tamper detected by the verifier", 12.5, {})]},
    ])
    textbox(s, 702, 484, 514, 46, [
        {"runs": [("DATA ACCESS   ", 10.5, {"bold": True, "color": AMBER}),
                  ("the AICTE master is public data and is not redistributed here; the 367-variant test set is ours "
                   "and ships with the repo.", 10.5, {"color": MUTED})], "line": 1.1},
    ])
    textbox(s, 48, 588, 600, 64, [
        {"runs": [("Nothing to host, nothing to log into, and nothing that can time out in front of a jury.",
                   13, {"bold": True, "color": DEEP})], "line": 1.14},
    ])
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
