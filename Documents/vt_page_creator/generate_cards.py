"""
generate_cards.py
-----------------
Reads a Markdown file and automatically flows the content across
4 cards (98 × 125 mm each) in a 2×2 grid on A4 pages. If the
content fills more than 4 cards, additional A4 pages are generated.

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
from reportlab.platypus import Paragraph, Frame, Spacer
from reportlab.lib.styles import ParagraphStyle

# ── Card dimensions ──────────────────────────────────────────────────────────

CARD_W = 98 * mm
CARD_H = 125 * mm

# ── A4 page ───────────────────────────────────────────────────────────────────

PAGE_W, PAGE_H = A4  # 595.28 × 841.89 pt

GRID_W = CARD_W * 2
GRID_H = CARD_H * 2
MARGIN_X = (PAGE_W - GRID_W) / 2
MARGIN_Y = (PAGE_H - GRID_H) / 2

# Card origins (bottom-left), row-major top→bottom
CARD_ORIGINS = [
    (MARGIN_X,          MARGIN_Y + CARD_H),  # top-left
    (MARGIN_X + CARD_W, MARGIN_Y + CARD_H),  # top-right
    (MARGIN_X,          MARGIN_Y),            # bottom-left
    (MARGIN_X + CARD_W, MARGIN_Y),            # bottom-right
]

PAD = 6 * mm

# ── Styles ────────────────────────────────────────────────────────────────────

def make_styles():
    h1 = ParagraphStyle("H1", fontSize=13, fontName="Helvetica-Bold",
                         leading=16, spaceAfter=4,
                         textColor=colors.HexColor("#111111"))
    h2 = ParagraphStyle("H2", fontSize=11, fontName="Helvetica-Bold",
                         leading=14, spaceAfter=3,
                         textColor=colors.HexColor("#333333"))
    body = ParagraphStyle("Body", fontSize=9, leading=13,
                           fontName="Helvetica", spaceAfter=4,
                           textColor=colors.HexColor("#1a1a1a"))
    bullet = ParagraphStyle("Bullet", fontSize=9, leading=13,
                              fontName="Helvetica", spaceAfter=2,
                              leftIndent=10, bulletIndent=0,
                              textColor=colors.HexColor("#1a1a1a"))
    return dict(h1=h1, h2=h2, body=body, bullet=bullet)


def _inline(text):
    """Convert **bold** and *italic* to ReportLab XML tags."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text)
    return text


def md_to_flowables(md_text, styles):
    """Lightweight Markdown → ReportLab flowables."""
    flowables = []
    for line in md_text.strip().splitlines():
        stripped = line.strip()
        if not stripped:
            flowables.append(Spacer(1, 3))
            continue
        if stripped.startswith("# "):
            flowables.append(Paragraph(_inline(stripped[2:]), styles["h1"]))
        elif stripped.startswith("## "):
            flowables.append(Paragraph(_inline(stripped[3:]), styles["h2"]))
        elif stripped.startswith(("- ", "* ")):
            flowables.append(Paragraph("• " + _inline(stripped[2:]), styles["bullet"]))
        else:
            flowables.append(Paragraph(_inline(stripped), styles["body"]))
    return flowables


def _make_frame(x, y):
    return Frame(
        x + PAD, y + PAD,
        CARD_W - 2 * PAD, CARD_H - 2 * PAD,
        leftPadding=0, rightPadding=0,
        topPadding=0, bottomPadding=0,
        showBoundary=0,
    )


def _draw_card_border(c, x, y):
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.setLineWidth(0.5)
    c.rect(x, y, CARD_W, CARD_H)


def _draw_crop_marks(c):
    """Crop marks at the four outer corners and centre edges of the grid."""
    mark = 5 * mm
    gap  = 2 * mm
    c.setStrokeColor(colors.HexColor("#999999"))
    c.setLineWidth(0.4)

    corners = [
        (MARGIN_X,          MARGIN_Y),
        (MARGIN_X + GRID_W, MARGIN_Y),
        (MARGIN_X,          MARGIN_Y + GRID_H),
        (MARGIN_X + GRID_W, MARGIN_Y + GRID_H),
    ]
    for cx, cy in corners:
        dx = -mark - gap if cx > PAGE_W / 2 else mark + gap
        c.line(cx + (gap if cx < PAGE_W / 2 else -gap), cy, cx + dx, cy)
        dy = -mark - gap if cy > PAGE_H / 2 else mark + gap
        c.line(cx, cy + (gap if cy < PAGE_H / 2 else -gap), cx, cy + dy)

    centre_x = MARGIN_X + CARD_W
    centre_y = MARGIN_Y + CARD_H
    for x, y in [(centre_x, MARGIN_Y - gap),
                 (centre_x, MARGIN_Y + GRID_H + gap),
                 (MARGIN_X - gap, centre_y),
                 (MARGIN_X + GRID_W + gap, centre_y)]:
        if x == centre_x:
            c.line(x, y, x, y + (-mark if y > PAGE_H / 2 else mark))
        else:
            c.line(x, y, x + (-mark if x > PAGE_W / 2 else mark), y)


def generate(input_md, output_pdf, draw_cutlines=True):
    styles = make_styles()

    with open(input_md, encoding="utf-8") as f:
        md_text = f.read()

    story = md_to_flowables(md_text, styles)

    c = canvas.Canvas(output_pdf, pagesize=A4)
    c.setTitle("4-up Cards")

    total_cards = 0
    page_num = 0

    while story:
        if page_num > 0:
            c.showPage()

        cards_on_page = 0
        for x, y in CARD_ORIGINS:
            if not story:
                break

            if draw_cutlines:
                _draw_card_border(c, x, y)

            frame = _make_frame(x, y)
            # addFromList removes items from story that fit into this frame
            frame.addFromList(story, c)
            cards_on_page += 1
            total_cards += 1

        if draw_cutlines:
            _draw_crop_marks(c)

        page_num += 1

    c.save()
    pages = page_num
    print(f"✅ Saved: {output_pdf}  ({total_cards} cards across {pages} page{'s' if pages != 1 else ''})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate 4-up card PDF from Markdown.")
    parser.add_argument("--input",       default="segments.md", help="Markdown file (default: segments.md)")
    parser.add_argument("--output",      default="cards.pdf",   help="Output PDF (default: cards.pdf)")
    parser.add_argument("--no-cutlines", action="store_true",   help="Omit cut guides")
    args = parser.parse_args()

    generate(args.input, args.output, draw_cutlines=not args.no_cutlines)
