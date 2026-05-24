# Survey Scripts

Utilities and notes for generating tables, plots, and exports for the survey material.

## Contents
- `Graphs.ipynb`: Notebook for plotting and analysis using `research_dataframe.csv`.
- `Md2Py.py`: Parses a Markdown table into a Python file with paper dictionaries and a Pandas helper.
- `Md2TeX.py`: Converts a Markdown table into LaTeX `tabular` sections.
- `Table.md`: Source Markdown table.
- `Table.py`: Generated Python output from `Table.md`.
- `Table.tex`: Generated LaTeX output from `Table.md`.
- `Images/`: Exported table images or figures.

## Quick start
Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
python -m pip install -U pip pandas matplotlib pillow
```

## Usage
Convert the Markdown table to a Python file:

```bash
python Md2Py.py Table.md Table.py
```

Note: the script writes a `.py` file next to the input file (the output path is derived from `Table.md`).

Convert the Markdown table to LaTeX:

```bash
python Md2TeX.py Table.md > Table.tex
```

## Data
- `research_dataframe.csv` is the main dataset used by the notebook and plotting scripts. This file is generated in `Graphs.ipynb` from `Table.md`.

## Notes
- `Table.py` and `Table.tex` are generated artifacts. Re-run the conversion scripts after editing `Table.md`.

## Citing
If you use this repository or its data in your work, please cite the survey:
```
@misc{antunes2025fpgabasedneuralnetworkaccelerators,
      title={FPGA-Based Neural Network Accelerators for Space Applications: A Survey}, 
      author={Pedro Antunes and Artur Podobas},
      year={2025},
      eprint={2504.16173},
      archivePrefix={arXiv},
      primaryClass={cs.AR},
      url={https://arxiv.org/abs/2504.16173}, 
}
```