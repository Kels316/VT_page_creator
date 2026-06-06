# VT Page Creator

Generate a print-ready A4 PDF containing **4 cards** (each 98 × 125 mm) laid out in a 2 × 2 grid from a Markdown file. Content flows automatically across cards. Each card has a page number centred at the bottom. Cut along the guides to get four cards.

---

## Dependencies

- [Pandoc](https://pandoc.org/) — Markdown → LaTeX conversion
- [MacTeX](https://tug.org/mactex/) — provides `pdflatex` and `pdfjam`

```
brew install pandoc
# Then install MacTeX from https://tug.org/mactex/
```

---

## Quick Start

### 1. Write your content

Create any Markdown file. Content flows automatically across cards. Use `\pagebreak` on its own line to force a break to the next card.

```markdown
# Checklist Title

## Section One

- [ ] First item
- [ ] Second item

\pagebreak

## Section Two

- [ ] Third item
```

Supported Markdown:

| Markdown        | Result                  |
| --------------- | ----------------------- |
| `# Heading`     | Large bold title        |
| `## Subheading` | Smaller bold heading    |
| `- [ ] item`    | Checkbox item           |
| `- item`        | Bullet point            |
| `**text**`      | Bold                    |
| `*text*`        | Italic                  |
| `---`           | Em-dash (in text)       |
| `\pagebreak`    | Force next card         |

### 2. Generate the PDF

```
python3 generate_cards.py --input my_file.md --output cards.pdf
```

---

## Options

```
python3 generate_cards.py [--input FILE] [--output FILE] [--no-cutlines]
```

| Flag            | Default       | Description                          |
| --------------- | ------------- | ------------------------------------ |
| `--input`       | `segments.md` | Path to your Markdown file           |
| `--output`      | `cards.pdf`   | Path for the output PDF              |
| `--no-cutlines` | off           | Omit the grey card borders           |

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

Content flows left-to-right, top-to-bottom. If your content exceeds 4 cards, additional A4 pages are generated automatically.

---

## Pipeline

1. **Pandoc** converts Markdown → LaTeX (handles checkboxes, bold, italic, em-dashes)
2. **pdflatex** renders each card as a 98 × 125 mm page
3. **pdfjam** imposes 4 pages onto one A4 sheet in a 2 × 2 grid
