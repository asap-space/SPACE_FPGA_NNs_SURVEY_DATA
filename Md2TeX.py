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
def _wrap_text(text: str, max_len: int = 20) -> str:
    parts = text.split("\\\\")
    wrapped_parts = []
    for part in parts:
        words = part.split()
        lines = []
        current_line = ""
        for word in words:
            if not current_line:
                current_line = word
            elif len(current_line) + 1 + len(word) > max_len:
                lines.append(current_line)
                current_line = word
            else:
                current_line += " " + word
        if current_line:
            lines.append(current_line)
        wrapped_parts.append("\\\\".join(lines))
    return "\\\\".join(wrapped_parts)

def _escape(text: str) -> str:
    """Escape LaTeX-special characters inside *text*."""
    out = text.replace("\\*", "*")
    out = out.replace("\\_", "_")
    out = out.replace("\\%", "%")
    out = out.replace("%", "\\%")
    out = out.replace("\\>", ">")
    out = out.replace("<br>", "\\\\")
    out = out.replace("BRAM_", "BRAM\\_")
    out = out.replace(" E^2", " E\\^2")
    return out.strip()


def _alignment_code(header_cells) -> str:
    return "l" * len(header_cells)


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
        escaped_cells = []
        for c in cells:
            c_str = c.strip()
            esc_c = _escape(c_str)
            # Apply wrapping mapping for max 20 chars
            esc_c = _wrap_text(esc_c, 20)
            if is_header:
                esc_c = f"\\textbf{{{esc_c}}}"
            if len(c_str) > 15 or "\\\\" in esc_c:
                esc_c = f"\\makecell[tl]{{{esc_c}}}"
            escaped_cells.append(esc_c)
        return " & ".join(escaped_cells) + r" \\ \hline"

    def _create_table(header_cells: List[str], data_rows: List[List[str]]) -> str:
        rows: List[str] = [
            _to_row(header_cells, is_header=True),
        ]
        for row in data_rows:
            rows.append(_to_row(row))

        body = "\n".join(rows)
        colspec = _alignment_code(header_cells)
        return (
            "\\begin{center}\n"
            "\\scalebox{0.6}{\n"
            "\\renewcommand{\\arraystretch}{1.3}\n"
            f"\\begin{{tabular}}{{{colspec}}}\n\\hline\n{body}\n\\end{{tabular}}\n"
            "}\n"
            "\\end{center}"
        )

    algo_cols = slice(1, 16)
    hw_cols = lambda r: [r[1]] + r[16:]

    parsed_data_rows = [[c.strip() for c in row.strip("|").split("|")] for row in data_rows]

    algo_header = header_cells[algo_cols]
    algo_data = [row[algo_cols] for row in parsed_data_rows]
    algo_tex = "\\section{Algorithm-related table}\\label{app:algorithm_table}\n" + _create_table(algo_header, algo_data)

    hw_header = hw_cols(header_cells)
    hw_data = [hw_cols(row) for row in parsed_data_rows]
    hw_tex = "\\section{Hardware-related table}\\label{app:hardware_table}\n" + _create_table(hw_header, hw_data)

    return algo_tex + "\n\n" + hw_tex


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
