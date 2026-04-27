from __future__ import annotations

from pathlib import Path


ALG_COLS = list(range(0, 16))
HW_COLS = [1] + list(range(16, 31))

ALG_SPEC = "|p{10pt}|p{15pt}|p{4pt}|p{11pt}|p{34pt}|p{17pt}|p{18pt}|p{9pt}|p{18pt}|p{10pt}|p{20pt}|p{32pt}|p{14pt}|p{26pt}|p{28pt}|p{21pt}|"
HW_SPEC = "|p{15pt}|p{5pt}|p{4pt}|p{14pt}|p{26pt}|p{34pt}|p{17pt}|p{32pt}|p{18pt}|p{30pt}|p{10pt}|p{22pt}|p{20pt}|p{32pt}|p{38pt}|p{5pt}|"

ALG_HEADER = [
    r"\textbf{Paper Name}",
    r"\textbf{Citation\newline Key}",
    r"\textbf{Year}",
    r"\textbf{Application}",
    r"\textbf{Data Origin\newline (In-situ vs Remote)}",
    r"\textbf{Network\newline Type/s}",
    r"\textbf{NN\newline Architecture}",
    r"\textbf{Dataset/s}",
    r"\textbf{Training\newline Method}",
    r"\textbf{Input Size}",
    r"\textbf{No. of\newline parameters}",
    r"\textbf{Quantization\newline (aka, Precision)}",
    r"\textbf{Memory\newline Size}",
    r"\textbf{Operations\newline (OP or FLOP)}",
    r"\textbf{PTQ, QAT,\newline or\newline Finetuned}",
    r"\textbf{Classification\newline (\%)}",
]

HW_HEADER = [
    r"\textbf{Citation\newline Key}",
    r"\textbf{Board}",
    r"\textbf{FPGA}",
    r"\textbf{FPGA\newline Vendor}",
    r"\textbf{Hardware\newline Implementation}",
    r"\textbf{Accelerator's\newline Main Architecture}",
    r"\textbf{Model Flexibility}",
    r"\textbf{FPGA\newline Resources\newline Consumption}",
    r"\textbf{Frequency\newline (MHz)}",
    r"\textbf{Inference\newline Time\newline (Latency)}",
    r"\textbf{Throughput}",
    r"\textbf{Performance\newline (GOP/s)}",
    r"\textbf{Power\newline Consumption}",
    r"\textbf{Power\newline Efficiency\newline (GOP/s/W)}",
    r"\textbf{Per-inference\newline Energy\newline Consumption}",
    r"\textbf{Notes}",
]


def _find_first_index(lines: list[str], predicate) -> int:
    for i, line in enumerate(lines):
        if predicate(line):
            return i
    raise ValueError("No matching line found")


def _parse_rows(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in lines:
        row = row.rstrip()
        if not row:
            continue
        if not row.endswith(r"\\ \hline"):
            raise ValueError(f"Unexpected row termination: {row[-120:]}")
        core = row[: -len(r"\\ \hline")].rstrip()
        cells = [c.strip() for c in core.split(" & ")]
        if len(cells) != 31:
            raise ValueError(f"Row has {len(cells)} cells, expected 31")
        rows.append(cells)
    return rows


def _emit_table(spec: str, header: list[str], rows: list[list[str]], cols: list[int]) -> str:
    out: list[str] = []
    out.append(rf"\begin{{tabular}}{{{spec}}}")
    out.append(r"\toprule")
    out.append(" & ".join(header) + r" \\ \midrule")
    for row in rows:
        out.append(" & ".join(row[i] for i in cols) + r" \\ \hline")
    out.append(r"\bottomrule")
    out.append(r"\end{tabular}")
    return "\n".join(out) + "\n"


def split_table(src_path: Path) -> tuple[str, str]:
    src = src_path.read_text(encoding="utf-8")
    lines = src.splitlines()

    begin_i = _find_first_index(lines, lambda l: l.lstrip().startswith(r"\begin{tabular}{"))
    end_i = _find_first_index(lines, lambda l: l.strip() == r"\end{tabular}")

    header_i = _find_first_index(lines[begin_i:end_i + 1], lambda l: r"\midrule" in l)
    header_i = begin_i + header_i

    bottom_i = _find_first_index(lines[header_i:end_i + 1], lambda l: l.strip() == r"\bottomrule")
    bottom_i = header_i + bottom_i

    body_lines = lines[header_i + 1 : bottom_i]
    rows = _parse_rows(body_lines)

    alg = _emit_table(ALG_SPEC, ALG_HEADER, rows, ALG_COLS)
    hw = _emit_table(HW_SPEC, HW_HEADER, rows, HW_COLS)
    return alg, hw


def main() -> None:
    base = Path(__file__).resolve().parent

    src = base / "Table_full.tex"
    if not src.exists():
        # Default to Table.tex and create a backup
        src = base / "Table.tex"
        backup = base / "Table_full.tex"
        if not backup.exists():
            backup.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    alg, hw = split_table(src)

    (base / "Table_algorithm.tex").write_text(alg, encoding="utf-8")
    (base / "Table_hardware.tex").write_text(hw, encoding="utf-8")

    combined = (
        "% Algorithm-related table (ends at Classification)\n"
        + alg
        + "\n% Hardware-related table (starts at Citation Key, then Board...Notes)\n"
        + hw
    )
    (base / "Table.tex").write_text(combined, encoding="utf-8")

    print("OK: wrote Table_algorithm.tex, Table_hardware.tex, and Table.tex")


if __name__ == "__main__":
    main()
