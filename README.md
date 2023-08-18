# `eda-report` - Automated Exploratory Data Analysis

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Tim-Abwao/eda-report/HEAD?filepath=eda-report-basics.ipynb)
[![PyPI version](https://badge.fury.io/py/eda-report.svg)](https://badge.fury.io/py/eda-report)
[![Python 3.9 - 3.11](https://github.com/Tim-Abwao/eda-report/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/Tim-Abwao/eda-report/actions/workflows/unit-tests.yml)
[![Documentation Status](https://readthedocs.org/projects/eda-report/badge/?version=latest)](https://eda-report.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/Tim-Abwao/eda-report/branch/main/graph/badge.svg?token=KNQD8XZCWG)](https://codecov.io/gh/Tim-Abwao/eda-report)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python program to help automate the exploratory data analysis and reporting process.

Input data is analyzed using [pandas][pandas] and [SciPy][scipy]. Graphs are plotted using [matplotlib][matplotlib]. The results are then nicely packaged as a *Word (.docx)* document using [python-docx][python-docx].

![screencast of report document from iris dataset][report-screencast]

## Installation

You can install the package from [PyPI][eda-report-pypi] using:

```bash
pip install eda-report
```

## Basic Usage

### 1. Graphical User Interface

The `eda-report` command launches a graphical window to help select a `csv`/`excel` file to analyze:

```bash
eda-report
```

![screencast of the gui][gui-screencast]

You'll be prompted to set a *report title*, *group-by/target variable (optional)*, *graph color* and *output filename*; after which the contents of the input file are analyzed, and the results saved in a *Word (.docx)* document.

>**NOTE:** For help with `Tk` - related issues, consider visiting [TkDocs][tkdocs].

### 2. Command Line Interface

```bash
$ eda-report -i iris.csv -o iris-report.docx
Analyze variables:  100%|███████████████████████████████████| 5/5
Plot variables:     100%|███████████████████████████████████| 5/5
Bivariate analysis: 100%|███████████████████████████████████| 6/6 pairs.
[INFO 02:12:22.146] Done. Results saved as 'iris-report.docx'
```

```bash
$ eda-report -h
usage: eda-report [-h] [-i INFILE] [-o OUTFILE] [-t TITLE] [-c COLOR]
                  [-g GROUPBY]

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
  -g GROUPBY, -T GROUPBY, --groupby GROUPBY, --target GROUPBY
                        The variable to use for grouping plotted values. An
                        integer value is treated as a column index, whereas a
                        string is treated as a column label.
```

</details>

### 3. Interpreter Session

```python
>>> eda_report.summarize(iris_data)

                  Summary Statistics for Numeric features (4)
                  -------------------------------------------
                count     avg  stddev  min  25%   50%  75%  max  skewness  kurtosis
  sepal_length    150  5.8433  0.8281  4.3  5.1  5.80  6.4  7.9    0.3149   -0.5521
  sepal_width     150  3.0573  0.4359  2.0  2.8  3.00  3.3  4.4    0.3190    0.2282
  petal_length    150  3.7580  1.7653  1.0  1.6  4.35  5.1  6.9   -0.2749   -1.4021
  petal_width     150  1.1993  0.7622  0.1  0.3  1.30  1.8  2.5   -0.1030   -1.3406

                Summary Statistics for Categorical features (1)
                -----------------------------------------------
                    count unique     top freq relative freq
            species   150      3  setosa   50        33.33%


                        Pearson's Correlation (Top 20)
                        ------------------------------
      petal_length & petal_width -> very strong positive correlation (0.96)
     sepal_length & petal_length -> very strong positive correlation (0.87)
      sepal_length & petal_width -> very strong positive correlation (0.82)
      sepal_width & petal_length -> moderate negative correlation (-0.43)
       sepal_width & petal_width -> weak negative correlation (-0.37)
      sepal_length & sepal_width -> very weak negative correlation (-0.12)
```

Check out the [documentation][docs] for more features and details.

[docs]: https://eda-report.readthedocs.io/
[eda-report-pypi]: https://pypi.org/project/eda-report/
[matplotlib]: https://matplotlib.org/
[pandas]: https://pandas.pydata.org/
[python-docx]: https://python-docx.readthedocs.io/
[scipy]: https://scipy.org/
[gui-screencast]: https://raw.githubusercontent.com/Tim-Abwao/eda-report/dev/docs/source/_static/screencast.gif
[report-screencast]: https://raw.githubusercontent.com/Tim-Abwao/eda-report/dev/docs/source/_static/report.gif
[tkdocs]: https://tkdocs.com/index.html
