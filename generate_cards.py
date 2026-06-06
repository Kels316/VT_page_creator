"""
generate_cards.py
-----------------
Reads segments.md (split on '---' separators) and renders
4 cards (98 x 125 mm each) in a 2×2 grid on a single A4 page.

The page is designed so you can cut along the grid lines
to get exactly 4 cards.

Usage:
    python3 generate_cards.py
    python3 generate_cards.py --input my_file.md --output my_cards.pdf

Dependencies:
    pip install reportlab markdown
"""

import argparse
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame, KeepInFrame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT


# ── Card dimensions ──────────────────────────────────────────────────────────
CARD_W = 98 * mm
CARD_H = 125 * mm

# ── A4 page ───────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4   # 595.28 × 841.89 pt

# Centre the 2×2 grid on the page
GRID_W = CARD_W * 2
GRID_H = CARD_H * 2
MARGIN_X = (PAGE_W - GRID_W) / 2
MARGIN_Y = (PAGE_H - GRID_H) / 2

# Card origins (bottom-left of each card), row-major order top→bottom
CARD_ORIGINS = [
    (MARGIN_X,          MARGIN_Y + CARD_H),   # top-left
    (MARGIN_X + CARD_W, MARGIN_Y + CARD_H),   # top-right
    (MARGIN_X,          MARGIN_Y),             # bottom-left
    (MARGIN_X + CARD_W, MARGIN_Y),             # bottom-right
]

# ── Padding inside each card ──────────────────────────────────────────────────
PAD = 6 * mm

# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    base = dict(fontName="Helvetica", leading=14, textColor=colors.HexColor("#1a1a1a"))

    h1 = ParagraphStyle("H1", fontSize=13, fontName="Helvetica-Bold",
                        leading=16, spaceAfter=4,
                        textColor=colors.HexColor("#111111"))
    h2 = ParagraphStyle("H2", fontSize=11, fontName="Helvetica-Bold",
                        leading=14, spaceAfter=3,
                        textColor=colors.HexColor("#333333"))
    body = ParagraphStyle("Body", fontSize=9, leading=13,
                          fontName="Helvetica", spaceAfter=4,
                          textColor=colors.HexColor("#1a1a1a"))
    bold = ParagraphStyle("Bold", fontSize=9, leading=13,
                          fontName="Helvetica-Bold", spaceAfter=4,
                          textColor=colors.HexColor("#1a1a1a"))
    bullet = ParagraphStyle("Bullet", fontSize=9, leading=13,
                            fontName="Helvetica", spaceAfter=2,
                            leftIndent=10, bulletIndent=0,
                            textColor=colors.HexColor("#1a1a1a"))
    return dict(h1=h1, h2=h2, body=body, bold=bold, bullet=bullet)


def md_to_paragraphs(md_text, styles):
    """Very lightweight Markdown → ReportLab Paragraph converter."""
    paragraphs = []
    for line in md_text.strip().splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            text = _inline(stripped[2:])
            paragraphs.append(Paragraph(text, styles["h1"]))
        elif stripped.startswith("## "):
            text = _inline(stripped[3:])
            paragraphs.append(Paragraph(text, styles["h2"]))
        elif stripped.startswith(("- ", "* ")):
            text = "• " + _inline(stripped[2:])
            paragraphs.append(Paragraph(text, styles["bullet"]))
        else:
            text = _inline(stripped)
            paragraphs.append(Paragraph(text, styles["body"]))
    return paragraphs


def _inline(text):
    """Convert **bold** and *italic* to ReportLab XML tags."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text)
    return text


def parse_segments(md_path):
    """Split the markdown file on '---' lines into up to 4 segments."""
    with open(md_path, encoding="utf-8") as f:
        raw = f.read()
    segments = re.split(r'\n---\n', raw)
    segments = [s.strip() for s in segments if s.strip()]
    if len(segments) > 4:
        print(f"⚠  Found {len(segments)} segments; only the first 4 will be used.")
    return segments[:4]


def draw_card(c, x, y, paragraphs, index, draw_cutlines=True):
    """Draw one card at canvas position (x, y) = bottom-left corner."""
    # ── optional light border / cut guide ────────────────────────────────────
    if draw_cutlines:
        c.setStrokeColor(colors.HexColor("#cccccc"))
        c.setLineWidth(0.5)
        c.rect(x, y, CARD_W, CARD_H)

    # ── flow text into a Frame ────────────────────────────────────────────────
    frame = Frame(
        x + PAD, y + PAD,
        CARD_W - 2 * PAD, CARD_H - 2 * PAD,
        leftPadding=0, rightPadding=0,
        topPadding=0, bottomPadding=0,
        showBoundary=0,
    )
    story = KeepInFrame(CARD_W - 2 * PAD, CARD_H - 2 * PAD, paragraphs,
                        mode="shrink")
    frame.addFromList([story], c)


def generate(input_md, output_pdf, draw_cutlines=True):
    styles = make_styles()
    segments = parse_segments(input_md)

    if len(segments) < 4:
        print(f"ℹ  Only {len(segments)} segment(s) found; remaining cards will be blank.")

    c = canvas.Canvas(output_pdf, pagesize=A4)
    c.setTitle("4-up Cards")

    for i, (x, y) in enumerate(CARD_ORIGINS):
        if i < len(segments):
            paras = md_to_paragraphs(segments[i], styles)
        else:
            paras = [Paragraph("(empty)", styles["body"])]
        draw_card(c, x, y, paras, i, draw_cutlines=draw_cutlines)

    # ── cut-line cross marks at corners of grid ───────────────────────────────
    if draw_cutlines:
        _draw_crop_marks(c)

    c.save()
    print(f"✅  Saved: {output_pdf}")


def _draw_crop_marks(c):
    """Draw small crop/cut marks at the four outer corners of the grid."""
    mark = 5 * mm
    gap  = 2 * mm
    c.setStrokeColor(colors.HexColor("#999999"))
    c.setLineWidth(0.4)

    corners = [
        (MARGIN_X, MARGIN_Y),                         # bottom-left
        (MARGIN_X + GRID_W, MARGIN_Y),                 # bottom-right
        (MARGIN_X, MARGIN_Y + GRID_H),                 # top-left
        (MARGIN_X + GRID_W, MARGIN_Y + GRID_H),        # top-right
    ]
    for cx, cy in corners:
        # horizontal tick
        dx = -mark - gap if cx > PAGE_W / 2 else mark + gap
        c.line(cx + (gap if cx < PAGE_W / 2 else -gap),
               cy, cx + dx, cy)
        # vertical tick
        dy = -mark - gap if cy > PAGE_H / 2 else mark + gap
        c.line(cx, cy + (gap if cy < PAGE_H / 2 else -gap),
               cx, cy + dy)

    # centre cross marks (between cards)
    centre_x = MARGIN_X + CARD_W
    centre_y = MARGIN_Y + CARD_H
    for x, y in [(centre_x, MARGIN_Y - gap), (centre_x, MARGIN_Y + GRID_H + gap),
                 (MARGIN_X - gap, centre_y), (MARGIN_X + GRID_W + gap, centre_y)]:
        if x == centre_x:
            c.line(x, y, x, y + (-mark if y > PAGE_H/2 else mark))
        else:
            c.line(x, y, x + (-mark if x > PAGE_W/2 else mark), y)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate 4-up card PDF from Markdown.")
    parser.add_argument("--input",  default="segments.md",  help="Markdown file (default: segments.md)")
    parser.add_argument("--output", default="cards.pdf",    help="Output PDF (default: cards.pdf)")
    parser.add_argument("--no-cutlines", action="store_true", help="Omit cut guides")
    args = parser.parse_args()

    generate(args.input, args.output, draw_cutlines=not args.no_cutlines)
