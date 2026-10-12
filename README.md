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
@article{10.1145/3857797,
  author = {Antunes, Pedro and Podobas, Artur},
  title = {FPGA-Based Neural Network Accelerators for Space Missions: A Survey},
  year = {2026},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  issn = {0360-0300},
  url = {https://doi.org/10.1145/3857797},
  doi = {10.1145/3857797},
  abstract = {Space missions are growing ever more ambitious, placing greater demands on onboard computing. Field-programmable gate arrays (FPGAs) have garnered interest due to their reconfigurability and cost-effectiveness. At the same time, neural network (NN)-based methods are proving invaluable for critical spacecraft tasks such as autonomous operations, remote sensing, selective downlink, and data compression. This survey reviews and classifies the state of the art in FPGA-based NN accelerators for space missions. We examine current trends, highlight key challenges, and suggest directions for future research. This work highlights key aspects for integrating high-performance NN acceleration into next-generation spacecraft computing systems.},
  note = {Just Accepted},
  journal = {ACM Comput. Surv.},
  month = oct,
  keywords = {Field Programmable Gate Arrays (FPGAs), Deep Learning, Onboard Processing, Space Missions, Edge AI, Fault Tolerance}
}
```
