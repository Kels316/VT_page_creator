# VT Page Creator

Generate a print-ready A4 PDF containing **4 cards** (each 98 × 125 mm) laid out in a 2 × 2 grid from a simple Markdown file. Cut along the guides to get four identical-sized cards.

---

## Quick Start

### 1. Install dependencies

```bash
pip install reportlab markdown
```

### 2. Edit your content

Open `segments.md` and fill in your four sections, separated by `---`:

```markdown
# Card Title
**Label:** Value
Some body text here.

- Bullet one
- Bullet two

---

# Second Card
...
```

Each section between `---` dividers becomes one card. You can use:

| Markdown | Result |
|---|---|
| `# Heading` | Large bold title |
| `## Subheading` | Smaller bold heading |
| `- item` or `* item` | Bullet point |
| `**text**` | Bold |
| `*text*` | Italic |

### 3. Generate the PDF

```bash
python3 generate_cards.py
```

This produces `cards.pdf` — ready to print on A4 and cut.

---

## Options

```
python3 generate_cards.py [--input FILE] [--output FILE] [--no-cutlines]
```

| Flag | Default | Description |
|---|---|---|
| `--input` | `segments.md` | Path to your Markdown file |
| `--output` | `cards.pdf` | Path for the output PDF |
| `--no-cutlines` | off | Omit the grey borders and crop marks |

**Examples:**

```bash
# Custom file names
python3 generate_cards.py --input my_labels.md --output labels.pdf

# No cut guides (e.g. for borderless printing)
python3 generate_cards.py --no-cutlines
```

---

## Card Layout

```
┌─────────────────────────┐
│  A4 page (210 × 297 mm) │
│  ┌──────────┬──────────┐ │
│  │  Card 1  │  Card 2  │ │
│  │ 98×125mm │ 98×125mm │ │
│  ├──────────┼──────────┤ │
│  │  Card 3  │  Card 4  │ │
│  │ 98×125mm │ 98×125mm │ │
│  └──────────┴──────────┘ │
└─────────────────────────┘
```

The grid is centred on the page. Crop marks appear at the outer corners and between cards so you can cut accurately.

If fewer than 4 segments are defined in your Markdown file, the remaining card slots will be left blank. If more than 4 are defined, only the first 4 are used.

---

## Files

| File | Purpose |
|---|---|
| `generate_cards.py` | Main script |
| `segments.md` | Template content file — edit this |

---

## Requirements

- Python 3.8+
- `reportlab` — PDF generation
- `markdown` — Markdown parsing
