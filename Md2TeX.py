# md2latex.py
"""md2latex.py - Convert a pipe-delimited Markdown table file to a LaTeX
`tabular` environment.

The script is intentionally minimal: **give it one argument - the path to a
`.md` file that contains exactly one table - and it prints the LaTeX code to
stdout**. No other options needed.

Example
-------
```bash
python md2latex.py Table.md  >  Table.tex
```

If you prefer to call it from Python code, import the `markdown_table_to_latex`
function and pass the path:

```python
from md2latex import markdown_table_to_latex
latex = markdown_table_to_latex("Table.md")
print(latex)
```
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _escape(text: str) -> str:
    """Escape LaTeX-special characters inside *text*."""
    out = text.replace("\\*", "*")
    #out = out.replace("\\\\", "\\")
    #out = out.replace("\\|", "|")
    out = out.replace("\\_", "_")
    out = out.replace("\\%", "%")
    out = out.replace("%", "\\%")
    out = out.replace("\\>", ">")
    out = out.replace("<br>", "\\newline ")
    out = out.replace("BRAM_", "BRAM\\_")
    out = out.replace(" E^2", " E\\^2")
    return out.strip()


def _alignment_code(header_cells) -> str:
    # Calculate column widths based on header lengths
    header_lengths = [len(cell) for cell in header_cells]
    # Create column specification with paragraph columns
    colspec_parts = [f"p{{{width}pt}}" for width in header_lengths]
    colspec = "|" + "|".join(colspec_parts) + "|"
    return colspec


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def markdown_table_to_latex(path: str | Path) -> str:
    path = Path(path)
    if not path.is_file():  # pragma: no cover
        raise FileNotFoundError(path)

    # Read and keep only non‑blank lines.
    lines: List[str] = [
        ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    if len(lines) < 2:
        raise ValueError("File doesn't appear to contain a markdown table")

    header, separator, *data_rows = lines

    header_cells = [c.strip() for c in header.strip("|").split("|")]
    separator_cells = [c.strip() for c in separator.strip("|").split("|")]

    def _to_row(cells: List[str], is_header: bool = False) -> str:
        if is_header:
            escaped_cells = [f"\\textbf{{{_escape(c)}}}" for c in cells]
        else:
            escaped_cells = [_escape(c) for c in cells]
        return " & ".join(escaped_cells) + r" \\ \hline"

    rows: List[str] = [
        _to_row(header_cells, is_header=True),
    ]
    for row in data_rows:
        rows.append(_to_row([c.strip() for c in row.strip("|").split("|")]))

    body = "\n".join(rows)

    colspec = _alignment_code(header_cells)
    return f"\\begin{{tabular}}{{{colspec}}}\n\\hline\n{body}\n\\end{{tabular}}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def convert(file):
    """Decorator to allow the script to be run as a module."""
    path = Path(file)
    latex_output = markdown_table_to_latex(file)
    output_path = path.with_suffix(".tex")
    output_path.write_text(latex_output, encoding="utf-8")


def _main() -> None:  # pragma: no cover
    if len(sys.argv) != 2 or sys.argv[1] in {"-h", "--help"}:
        print("Usage: python md2latex.py <table.md>", file=sys.stderr)
        sys.exit(1 if len(sys.argv) != 2 else 0)

    print(markdown_table_to_latex(sys.argv[1]))


if __name__ == "__main__":  # pragma: no cover
    _main()
