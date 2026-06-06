# VT Page Creator

Generate a print-ready A4 PDF containing **4 cards** (each 98 × 125 mm) laid out in a 2 × 2 grid from a Markdown file. Content flows automatically across cards — no manual separators needed. Cut along the guides to get four identical-sized cards.

---

## Quick Start

### 1. Install dependencies

```
pip install reportlab markdown
```

### 2. Write your content

Create any Markdown file. The script automatically flows the text across cards — if your content fills 3 cards, it uses 3 cards; if it fills more than 4, it generates additional A4 pages.

```markdown
# Card Title

Some body text here.

- Bullet one
- Bullet two

## Subheading

More content that will flow naturally into the next card when this one is full.
```

Supported Markdown:

| Markdown             | Result               |
| -------------------- | -------------------- |
| `# Heading`          | Large bold title     |
| `## Subheading`      | Smaller bold heading |
| `- item` or `* item` | Bullet point         |
| `**text**`           | Bold                 |
| `*text*`             | Italic               |

### 3. Generate the PDF

```
python3 generate_cards.py
```

This produces `cards.pdf` — ready to print on A4 and cut.

---

## Options

```
python3 generate_cards.py [--input FILE] [--output FILE] [--no-cutlines]
```

| Flag            | Default       | Description                          |
| --------------- | ------------- | ------------------------------------ |
| `--input`       | `segments.md` | Path to your Markdown file           |
| `--output`      | `cards.pdf`   | Path for the output PDF              |
| `--no-cutlines` | off           | Omit the grey borders and crop marks |

**Examples:**

```
# Custom file names
python3 generate_cards.py --input my_content.md --output labels.pdf

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

Content flows left-to-right, top-to-bottom. If your content exceeds 4 cards, additional A4 pages are generated with the same layout.

---

## Files

| File                | Purpose                                    |
| ------------------- | ------------------------------------------ |
| `generate_cards.py` | Main script                                |
| `segments.md`       | Example content file — replace or point `--input` at your own |

---

## Requirements

- Python 3.8+
- `reportlab` — PDF generation
- `markdown` — Markdown parsing
