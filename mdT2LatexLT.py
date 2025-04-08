import argparse
import re

def parse_markdown_table(content):
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    table_lines = []
    
    # Find table boundaries
    start = None
    for i, line in enumerate(lines):
        if line.startswith('|') and '---' in line and i > 0:
            start = i-1
            break
    if start is None:
        return None

    # Extract table components
    header = lines[start]
    separator = lines[start+1]
    rows = [line for line in lines[start+2:] if line.startswith('|')]

    # Parse alignment from separator
    alignments = []
    for cell in re.split(r'(?<!\\)\|', separator)[1:-1]:
        cell = cell.strip()
        if cell.startswith(':') and cell.endswith(':'):
            alignments.append('c')
        elif cell.startswith(':'):
            alignments.append('l')
        elif cell.endswith(':'):
            alignments.append('r')
        else:
            alignments.append('l')  # Default to left

    # Process headers and rows
    headers = [cell.strip() for cell in re.split(r'(?<!\\)\|', header)[1:-1]]
    processed_rows = []
    for row in rows:
        processed_rows.append([cell.strip() for cell in re.split(r'(?<!\\)\|', row)[1:-1]])

    return headers, alignments, processed_rows

def escape_latex(text):
    # Define the replacements, including multi-character tokens like '<br>'
    replacements = {
        '<br>': ' ',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}'
    }
    # Sort keys by length to ensure longer tokens (like '<br>') are matched before single characters
    keys = sorted(replacements.keys(), key=len, reverse=True)
    # Build a regex pattern that matches any of the keys
    pattern = re.compile('|'.join(map(re.escape, keys)))
    # Replace each occurrence with its corresponding LaTeX escape
    return pattern.sub(lambda match: replacements[match.group(0)], text)

def generate_latex_table(headers, alignments, rows):
    # Build column specification
    col_spec = '|'.join(alignments)
    col_spec = f'|{col_spec}|'

    # Build LaTeX code
    latex = [
        r"\begin{longtable}{" + col_spec + "}",
        r"\caption{Converted Table}\label{tab:converted}\\",
        r"\hline"
    ]

    # Header row
    escaped_headers = [rf"\textbf{{{escape_latex(h)}}}" for h in headers]
    latex.append(" & ".join(escaped_headers) + r" \\")
    latex.append(r"\hline")
    latex.append(r"\endfirsthead")

    # Subsequent page headers
    latex.append(r"\hline")
    latex.append(" & ".join(escaped_headers) + r" \\")
    latex.append(r"\hline")
    latex.append(r"\endhead")

    # Table footer
    latex.append(r"\hline")
    latex.append(r"\endfoot")

    # Data rows
    for row in rows:
        escaped_row = [escape_latex(cell) for cell in row]
        latex.append(" & ".join(escaped_row) + r" \\")
        latex.append(r"\hline")

    latex.append(r"\end{longtable}")
    return "\n".join(latex)

def main():
    parser = argparse.ArgumentParser(description='Convert Markdown table to LaTeX longtable')
    parser.add_argument('input_file', help='Input Markdown file')
    args = parser.parse_args()

    with open(args.input_file, 'r') as f:
        content = f.read()

    result = parse_markdown_table(content)
    if not result:
        print("No valid table found in the input file")
        return

    headers, alignments, rows = result

    # Replace the paper name with a placeholder "[0]" in the first column.
    if headers:
        headers[0] = "Ref."
    for row in rows:
        if row:
            row[0] = "[0]"

    latex_code = generate_latex_table(headers, alignments, rows)
    print(latex_code)

if __name__ == "__main__":
    main()
