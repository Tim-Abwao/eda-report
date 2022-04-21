# `eda-report` - Automated Exploratory Data Analysis

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Tim-Abwao/eda-report/HEAD?filepath=eda-report-basics.ipynb)
[![PyPI version](https://badge.fury.io/py/eda-report.svg)](https://badge.fury.io/py/eda-report)
[![Python 3.8 - 3.10](https://github.com/Tim-Abwao/eda-report/actions/workflows/test-python3.8-3.10.yml/badge.svg)](https://github.com/Tim-Abwao/eda-report/actions/workflows/test-python3.8-3.10.yml)
[![Documentation Status](https://readthedocs.org/projects/eda-report/badge/?version=latest)](https://eda-report.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/Tim-Abwao/eda-report/branch/main/graph/badge.svg?token=KNQD8XZCWG)](https://codecov.io/gh/Tim-Abwao/eda-report)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python program to help automate the exploratory data analysis and reporting process.

Input data is analyzed using [pandas][pandas] and [SciPy][scipy]. Graphs are plotted using [matplotlib][matplotlib] and [seaborn][seaborn]. The results are then nicely packaged as a *Word (.docx)* document using [python-docx][python-docx].

## Installation

You can install the package from [PyPI][eda-report-pypi] using:

```bash
pip install eda-report
```

## Basic Usage

### 1. Graphical User Interface

The `eda-report` command launches a graphical window to help select and analyze a `csv`/`excel` file:

```bash
eda-report
```

![screencast of the gui][screencast]

You will be prompted to set a *report title*, *target variable (optional, for grouping values)*, *graph color* and *output filename*, after which the contents of the input file will be analyzed, and the results will be saved in a *Word (.docx)* document.

>**NOTE:** For help with `Tk` - related issues, consider visiting [TkDocs][tkdocs].

### 2. Command Line Interface

To analyze a file named `input.csv`, just supply its path to the `eda-report` command:

```bash
eda-report -i input.csv
```

Or even:

```bash
eda-report -i input.csv -o output.docx -c cyan --title 'EDA Report'
```

For more details on the optional arguments, pass the `-h` or `--help` flag to view the *help message*:

```bash
eda-report -h
```

<details>

```bash
usage: eda-report [-h] [-i INFILE] [-o OUTFILE] [-t TITLE] [-c COLOR]
                  [-T TARGET]

Automatically analyze data and generate reports. A graphical user interface
will be launched if none of the optional arguments is specified.

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        A .csv or .xlsx file to analyze.
  -o OUTFILE, --outfile OUTFILE
                        The output name for analysis results (default: eda-
                        report.docx)
  -t TITLE, --title TITLE
                        The top level heading for the report (default:
                        Exploratory Data Analysis Report)
  -c COLOR, --color COLOR
                        The color to apply to graphs (default: cyan)
  -T TARGET, --target TARGET
                        The target variable (dependent feature), used to group
                        plotted values. An integer value is treated as a
                        column index, whereas a string is treated as a column
                        label.
```

</details>

### 3. Interactive Mode

#### 3.1 Analyze data

```python
>>> import eda_report
>>> from seaborn import load_dataset
>>> iris_data = load_dataset("iris")
>>> eda_report.summarize(iris_data)
                        OVERVIEW
                        ========
Numeric features: sepal_length, sepal_width, petal_length, petal_width
Categorical features: species
                          ***
          Summary Statistics (Numeric features)
          -------------------------------------
              count    mean     std  min  25%   50%  75%  max  skewness  kurtosis
sepal_length  150.0  5.8433  0.8281  4.3  5.1  5.80  6.4  7.9    0.3149   -0.5521
sepal_width   150.0  3.0573  0.4359  2.0  2.8  3.00  3.3  4.4    0.3190    0.2282
petal_length  150.0  3.7580  1.7653  1.0  1.6  4.35  5.1  6.9   -0.2749   -1.4021
petal_width   150.0  1.1993  0.7622  0.1  0.3  1.30  1.8  2.5   -0.1030   -1.3406
                          ***
          Summary Statistics (Categorical features)
          -----------------------------------------
        count unique     top freq relative freq
species   150      3  setosa   50        33.33%
                          ***
          Bivariate Analysis (Correlation)
          --------------------------------
sepal_length & petal_width --> strong positive correlation (0.82)
sepal_length & petal_length --> strong positive correlation (0.87)
petal_length & petal_width --> very strong positive correlation (0.96)
sepal_length & sepal_width --> very weak negative correlation (-0.12)
sepal_width & petal_width --> weak negative correlation (-0.37)
sepal_width & petal_length --> weak negative correlation (-0.43)
```

#### 3.2 Generate a report

```python
>>> eda_report.get_word_report(iris_data)
Analyze variables:  100%|███████████████████████████████████| 5/5
Plot variables:     100%|███████████████████████████████████| 5/5
Bivariate analysis: 100%|███████████████████████████████████| 6/6 pairs.
[INFO 16:14:53.648] Done. Results saved as 'eda-report.docx'
<eda_report.document.ReportDocument object at 0x7f196753bd60>
```

Visit the [official documentation][docs] for more details.

[docs]: https://eda-report.readthedocs.io/
[eda-report-pypi]: https://pypi.org/project/eda-report/
[matplotlib]: https://matplotlib.org/
[pandas]: https://pandas.pydata.org/
[python-docx]: https://python-docx.readthedocs.io/
[scipy]: https://scipy.org/
[screencast]: https://raw.githubusercontent.com/Tim-Abwao/eda-report/dev/docs/source/_static/screencast.gif
[seaborn]: https://seaborn.pydata.org/
[tkdocs]: https://tkdocs.com/index.html
