"""
generate_cards.py
-----------------
Pipeline:
  1. Pandoc converts Markdown → LaTeX (handles checkboxes, bold, italic, em-dashes)
  2. pdflatex renders each card as a 98×125mm page
  3. pdfjam imposes 4 pages onto one A4 sheet (2×2 grid)

Use \\pagebreak on its own line to force content onto the next card.
Content automatically flows onto the next card when a card is full.

Usage:
    python3 generate_cards.py
    python3 generate_cards.py --input my_file.md --output my_cards.pdf

Dependencies:
    brew install pandoc
    MacTeX — https://tug.org/mactex/  (provides pdflatex + pdfjam)
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile


# ---------------------------------------------------------------------------
# LaTeX template for small-page (98×125mm) card output
# ---------------------------------------------------------------------------

CARD_TEMPLATE = r"""
\documentclass[8pt]{article}
\usepackage[paperwidth=98mm, paperheight=125mm,
            top=7mm, bottom=7mm, left=7mm, right=7mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{amssymb}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}

\setcounter{secnumdepth}{0}
\setlength{\parindent}{0pt}
\setlength{\parskip}{1pt}

% Compact headings sized for 88mm text width
\usepackage{titlesec}
\titleformat{\section}{\normalsize\bfseries}{}{0em}{}
\titleformat{\subsection}{\small\bfseries}{}{0em}{}
\titleformat{\subsubsection}{\small\itshape\mdseries}{}{0em}{}
\titlespacing*{\section}{0pt}{4pt}{1pt}
\titlespacing*{\subsection}{0pt}{3pt}{1pt}
\titlespacing*{\subsubsection}{0pt}{2pt}{1pt}

% Checkbox lists
\setlist[itemize,1]{%
  label=$\square$, leftmargin=1.2em,
  itemsep=0pt, parsep=0pt, topsep=1pt, partopsep=0pt
}
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}%
}

\usepackage{eso-pic}
\pagestyle{empty}
% Page number pinned 3mm from bottom centre
\AddToShipoutPictureBG{%
  \AtPageLowerLeft{%
    \makebox[\paperwidth][c]{\raisebox{2mm}{\small\thepage}}%
  }%
}

\begin{document}
%%BODY%%
\end{document}
"""


def find_tool(name, extra_paths=None):
    """Find a CLI tool, checking extra_paths before $PATH."""
    for p in (extra_paths or []):
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return shutil.which(name)


def generate(input_md: str, output_pdf: str, draw_cutlines: bool = True):
    pandoc_paths = [
        "/opt/homebrew/bin/pandoc",
        "/usr/local/bin/pandoc",
    ]
    tex_paths = [
        "/Library/TeX/texbin/pdflatex",
        "/usr/local/texlive/2024/bin/universal-darwin/pdflatex",
        "/usr/local/texlive/2023/bin/universal-darwin/pdflatex",
    ]
    jam_paths = [
        "/Library/TeX/texbin/pdfjam",
        "/usr/local/texlive/2024/bin/universal-darwin/pdfjam",
        "/usr/local/texlive/2023/bin/universal-darwin/pdfjam",
    ]

    pandoc   = find_tool("pandoc",   pandoc_paths)
    pdflatex = find_tool("pdflatex", tex_paths)
    pdfjam   = find_tool("pdfjam",   jam_paths)

    if not pandoc:
        print("Error: pandoc not found. Install with: brew install pandoc",
              file=sys.stderr)
        sys.exit(1)

    if not pdflatex:
        print("Error: pdflatex not found. Install MacTeX from https://tug.org/mactex/",
              file=sys.stderr)
        sys.exit(1)
    if not pdfjam:
        print("Error: pdfjam not found. Install MacTeX from https://tug.org/mactex/",
              file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------ #
    # Step 1: Pandoc markdown → LaTeX body
    # ------------------------------------------------------------------ #
    result = subprocess.run(
        [pandoc, "--from=markdown+task_lists+smart", "--to=latex", input_md],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Pandoc error:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    body = result.stdout

    # \pagebreak in markdown ends up inside the last \item; move it to
    # after \end{itemize} so pdflatex produces a clean page break
    body = body.replace(r'\pagebreak', r'\newpage')
    body = re.sub(
        r'[ \t]*\\newpage[ \t]*\n(\\end\{itemize\})',
        r'\n\1\n\\newpage',
        body
    )

    latex = CARD_TEMPLATE.replace("%%BODY%%", body)

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = os.path.join(tmpdir, "cards.tex")
        tmp_pdf  = os.path.join(tmpdir, "cards.pdf")

        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(latex)

        # ------------------------------------------------------------------ #
        # Step 2: Compile to small-page PDF (98×125mm per page)
        # ------------------------------------------------------------------ #
        for _ in range(2):   # two passes for hyperref bookmarks
            r = subprocess.run(
                [pdflatex, "-interaction=nonstopmode",
                 "-output-directory", tmpdir, tex_file],
                capture_output=True, text=True
            )

        if not os.path.exists(tmp_pdf):
            print(f"pdflatex error:\n{r.stdout[-3000:]}", file=sys.stderr)
            sys.exit(1)

        # ------------------------------------------------------------------ #
        # Step 3: 4-up imposition onto A4 with pdfjam
        # ------------------------------------------------------------------ #
        # 2×98mm = 196mm, 2×125mm = 250mm — fits A4 with 7mm side margins
        # and 23.5mm top/bottom margins when noautoscale is set.
        # Give pdfjam a PATH that includes the TeX binaries
        tex_env = os.environ.copy()
        tex_env["PATH"] = os.path.dirname(pdflatex) + ":" + tex_env.get("PATH", "")

        frame_opts = ["--frame", "true"] if draw_cutlines else []
        result = subprocess.run(
            [pdfjam,
             "--nup",          "2x2",
             "--paper",        "a4paper",
             "--noautoscale",  "true",
             *frame_opts,
             "--outfile",      output_pdf,
             tmp_pdf],
            capture_output=True, text=True, env=tex_env
        )
        if result.returncode != 0:
            print(f"pdfjam error:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)

    print(f"✅ Saved: {output_pdf}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate 4-up card PDF from Markdown.")
    parser.add_argument("--input",       default="segments.md", help="Markdown file")
    parser.add_argument("--output",      default="cards.pdf",   help="Output PDF")
    parser.add_argument("--no-cutlines", action="store_true",   help="Omit cut guides")
    args = parser.parse_args()
    generate(args.input, args.output, draw_cutlines=not args.no_cutlines)
