# `eda-report` - Automated Exploratory Data Analysis

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Tim-Abwao/eda-report/HEAD?filepath=eda-report-basics.ipynb)
[![PyPI version](https://badge.fury.io/py/eda-report.svg)](https://badge.fury.io/py/eda-report)
[![Python 3.8 - 3.10](https://github.com/Tim-Abwao/eda-report/actions/workflows/test-python3.8-3.10.yml/badge.svg)](https://github.com/Tim-Abwao/eda-report/actions/workflows/test-python3.8-3.10.yml)
[![Documentation Status](https://readthedocs.org/projects/eda-report/badge/?version=latest)](https://eda-report.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/Tim-Abwao/eda-report/branch/main/graph/badge.svg?token=KNQD8XZCWG)](https://codecov.io/gh/Tim-Abwao/eda-report)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python program to help automate the exploratory data analysis and reporting process.

Input data is processed and analysed using [pandas][pandas]' built-in methods, and graphs are plotted using [matplotlib][matplotlib] & [seaborn][seaborn]. The results are then nicely packaged as a *Word (.docx)* document using [python-docx][python-docx].

## Installation

You can install the package from [PyPI][eda-report-pypi] using:

```bash
pip install eda-report
```

## Basic Usage

### 1. Graphical User Interface

The `eda-report` command launches a graphical window to help select and analyse a `csv`/`excel` file:

```bash
eda-report
```

![screencast of the gui][screencast]

You will be prompted to set a *report title*, *target variable (optional)*, *graph color* and *output filename*, after which the contents of the input file will be analysed, and the results will be saved in a *Word (.docx)* document.

>**NOTE:** For help with `Tk` - related issues, consider visiting [TkDocs][tkdocs].
### 2. Command Line Interface

To analyse a file named `input.csv`, just supply its path to the `eda-report` command:

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

Automatically analyse data and generate reports. A graphical user interface
will be launched if none of the optional arguments is specified.

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        A .csv or .xlsx file to analyse.
  -o OUTFILE, --outfile OUTFILE
                        The output name for analysis results (default: eda-
                        report.docx)
  -t TITLE, --title TITLE
                        The top level heading for the report (default:
                        Exploratory Data Analysis Report)
  -c COLOR, --color COLOR
                        The color to apply to graphs (default: cyan)
  -T TARGET, --target TARGET
                        The target variable (dependent feature), used to
                        color-code plotted values. An integer value is treated
                        as a column index, whereas a string is treated as a
                        column label.
```

</details>

### 3. Interactive Mode

#### 3.1 Analyse univariate data

```python
>>> from eda_report.univariate import Variable
>>> Variable(range(20), name="1 to 20")
        Overview
        ========
Name: 1 to 20
Type: numeric
Unique Values: 20 -> [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, [...]
Missing Values: None
          ***
      Summary Statistics
                         1 to 20
Number of observations  20.00000
Average                  9.50000
Standard Deviation       5.91608
Minimum                  0.00000
Lower Quartile           4.75000
Median                   9.50000
Upper Quartile          14.25000
Maximum                 19.00000
Skewness                 0.00000
Kurtosis                -1.20000
```

#### 3.2 Analyse multivariate data

```python
>>> from eda_report.multivariate import MultiVariable
>>> from seaborn import load_dataset
>>> data = load_dataset("iris")
>>> MultiVariable(data)
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
petal_length & petal_width --> very strong positive correlation (0.96)
sepal_length & petal_length --> strong positive correlation (0.87)
sepal_length & petal_width --> strong positive correlation (0.82)
sepal_length & sepal_width --> very weak negative correlation (-0.12)
sepal_width & petal_length --> weak negative correlation (-0.43)
sepal_width & petal_width --> weak negative correlation (-0.37)
```

#### 3.3 Generate a report

```python
>>> from eda_report import get_word_report
>>> from seaborn import load_dataset

>>> data = load_dataset("iris")
>>> get_word_report(data)
Bivariate analysis: 100%|███████████████████████████████████| 6/6 numeric pairs.
Univariate analysis: 100%|███████████████████████████████████| 5/5 features.
[INFO 17:31:37.880] Done. Results saved as 'eda-report.docx'
<eda_report.document.ReportDocument object at 0x7f3040c9bcd0>
```

Visit the [official documentation][docs] for more details.

[pandas]: https://pandas.pydata.org/
[matplotlib]: https://matplotlib.org/
[seaborn]: https://seaborn.pydata.org/
[python-docx]: https://python-docx.readthedocs.io/en/latest/
[eda-report-pypi]: https://pypi.org/project/eda-report/
[screencast]: https://raw.githubusercontent.com/Tim-Abwao/eda-report/dev/docs/source/_static/screencast.gif
[docs]: https://eda-report.readthedocs.io/
[tkdocs]: https://tkdocs.com/index.html
