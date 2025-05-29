import argparse
import re
from pathlib import Path


EXCLUDED_VALUES = {"-", "\\", "/", ""}


def clean_cell(s):
    """Convert string to appropriate data type (int, float, or string) with replacements"""
    out = s.replace("\\*", "*")
    out = out.replace("\\m", "m")
    out = out.replace("\\a", "a")
    out = out.replace("\\\\", "\\")
    out = out.replace("\\|", "|")
    out = out.replace("\\_", "_")
    out = out.replace("\\%", "%")
    out = out.replace("\\>", ">")
    out = out.replace("<br>", "\\n")
    return out.strip()


def parse_markdown_table(lines):
    """Parse markdown table from lines and return list of filtered dictionaries"""
    table_start = None
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("|") and i + 1 < len(lines) and "---" in lines[i + 1]:
            table_start = i
            break
    if table_start is None:
        raise ValueError("No table found in the markdown content.")

    header_line = lines[table_start].strip()
    data_lines = []
    for line in lines[table_start + 2 :]:
        line = line.strip()
        if line.startswith("|"):
            data_lines.append(line)
        else:
            break

    headers = [cell.strip() for cell in header_line.split("|")[1:-1]]

    papers = []
    for data_line in data_lines:
        cells = [clean_cell(cell) for cell in re.split(r"(?<!\\)\|", data_line)[1:-1]]
        paper = {}
        for header, value in zip(headers, cells):
            if value not in EXCLUDED_VALUES:
                paper[header] = value
        papers.append(paper)

    return headers, papers


def generate_python_code(headers, papers):
    """Generate Python code with dynamic class structure"""
    code_lines = [
        "import pandas as pd\n\n",
        "class PaperData:",
        "    def __init__(self):",
        "        self.data = {",
    ]

    # Add headers with proper escaping
    for header in headers:
        escaped_header = header.replace('"', '\\"')
        code_lines.append(f'            "{escaped_header}": [],')

    code_lines.extend(
        [
            "        }",
            "",
            "    def add_entry(self, new_entry):",
            "        for key in self.data:",
            "            self.data[key].append(new_entry.get(key, None))",
            "",
            "    def to_dataframe(self):",
            "        return pd.DataFrame(self.data)",
            "",
        ]
    )
    var_names = []

    for i, paper in enumerate(papers):
        var_name = f"paper_{i+1}"
        var_names.append(var_name)
        code_lines.append(f"{var_name} = {{")
        for key, value in paper.items():
            if isinstance(value, (int, float)):
                code_lines.append(f'    "{key}": {value},')
            else:
                escaped_value = str(value).replace('"', '\\"')
                code_lines.append(f'    "{key}": "{escaped_value}",')
        code_lines.append("}\n")

    # Add the papers list
    code_lines.append(f"papers_list = [{', '.join(var_names)}]")
    return "\n".join(code_lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def convert(file):
    """Decorator to allow the script to be run as a module."""
    path = Path(file)

    with open(path, "r") as f:
        lines = f.readlines()
    try:
        headers, papers = parse_markdown_table(lines)
    except ValueError as e:
        print(f"Error: {e}")
        return

    python_code = generate_python_code(headers, papers)
    output_path = path.with_suffix(".py")
    output_path.write_text(python_code, encoding="utf-8")
    print(f"Successfully generated {output_path} with {len(papers)} papers")


def main():
    parser = argparse.ArgumentParser(
        description="Parse markdown table to Python dictionaries with list"
    )
    parser.add_argument("input_file", help="Input markdown file path")
    parser.add_argument("output_file", help="Output Python file path")
    args = parser.parse_args()
    convert(args.input_file)


if __name__ == "__main__":
    main()
