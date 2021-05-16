# Automated Exploratory Data Analysis

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Tim-Abwao/auto-eda/HEAD?filepath=eda_report%20basics.ipynb)
[![PyPI version](https://badge.fury.io/py/eda-report.svg)](https://badge.fury.io/py/eda-report)
[![Python 3.8](https://github.com/Tim-Abwao/auto-eda/actions/workflows/run-tests.yml/badge.svg)](https://github.com/Tim-Abwao/auto-eda/actions/workflows/run-tests.yml)
[![Python 3.7 | 3.9](https://github.com/Tim-Abwao/auto-eda/actions/workflows/test-python3.7-3.9.yml/badge.svg)](https://github.com/Tim-Abwao/auto-eda/actions/workflows/test-python3.7-3.9.yml)
[![Documentation Status](https://readthedocs.org/projects/eda-report/badge/?version=latest)](https://eda-report.readthedocs.io/en/latest/?badge=latest)

A Python program to help automate the EDA process.

Data is analysed using [pandas][1]' built-in methods, and graphs are plotted using [matplotlib][3] & [seaborn][4]. The results are then nicely packaged as a *.docx* file using [python-docx][5].

## Installation

You can install the package from [PyPI][6] using:

```bash
pip install eda-report
```

## Basic Usage

### 1. Graphical User Interface

The `eda_report` command launches a graphical window to help select and analyse a `csv`/`excel` file:

```bash
eda_report
```

![screencast of the gui][screencast]

You will be prompted to set a *report title*, *graph color* and *output filename*, after which the contents of the input file will be analysed, and the results will be saved in *.docx* format.

### 2. Interactive Mode

You can obtain a summary for a *single feature (univariate)* using the `Variable` class:

```python
>>> from eda_report.univariate import Variable
>>> x = Variable(data=range(50), name='1 to 50')
>>> x
            Overview
            ========
Name: 1 to 50,
Type: numeric,
Unique Values: 50 -> {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, [...],
Missing Values: None

        Summary Statistics
        ==================
                         1 to 50
Number of observations  50.00000
Average                 24.50000
Standard Deviation      14.57738
Minimum                  0.00000
Lower Quartile          12.25000
Median                  24.50000
Upper Quartile          36.75000
Maximum                 49.00000
Skewness                 0.00000
Kurtosis                -1.20000

>>> x.show_graphs()
```

You can obtain statistics for a *set of features (multivariate)* using the `MultiVariable` class:

```python
>>> from eda_report.multivariate import MultiVariable
>>> # Get a dataset
>>> import seaborn as sns
>>> data = sns.load_dataset('iris')
>>> X = MultiVariable(data)
Bivariate analysis: 100%|████████████████████████████████████████████| 6/6 [00:01<00:00,  3.85it/s]
>>> X
        Overview
        ========
Numeric features: sepal_length, sepal_width, petal_length, petal_width
Categorical features: species

        Summary Statistics (Numeric features)
        =====================================
       sepal_length  sepal_width  petal_length  petal_width
count    150.000000   150.000000    150.000000   150.000000
mean       5.843333     3.057333      3.758000     1.199333
std        0.828066     0.435866      1.765298     0.762238
min        4.300000     2.000000      1.000000     0.100000
25%        5.100000     2.800000      1.600000     0.300000
50%        5.800000     3.000000      4.350000     1.300000
75%        6.400000     3.300000      5.100000     1.800000
max        7.900000     4.400000      6.900000     2.500000

        Summary Statistics (Categorical features)
        =========================================
       species
count      150
unique       3
top     setosa
freq        50

        Bivariate Analysis (Correlation)
        ================================
sepal_length & petal_width --> strong positive correlation (0.82)
sepal_width & petal_width --> weak negative correlation (-0.37)
sepal_length & sepal_width --> very weak negative correlation (-0.12)
sepal_length & petal_length --> strong positive correlation (0.87)
sepal_width & petal_length --> weak negative correlation (-0.43)
petal_length & petal_width --> very strong positive correlation (0.96)

>>> X.show_correlation_heatmap()
>>> # Generate a report document
>>> from eda_report import get_word_report
>>> get_word_report(data)
[INFO 10:56:50.241] Assessing correlation in numeric variables...
Bivariate analysis: 100%|████████████████████████████████████████████| 6/6 [00:01<00:00,  3.89it/s]
[INFO 10:56:53.851] Done. Summarising each variable...
Univariate analysis: 100%|███████████████████████████████████████████| 5/5 [00:01<00:00,  2.52it/s]
[INFO 10:56:56.007] Done. Results saved as 'eda-report.docx' 
```

### 3. Command Line Interface

To analyse a file named `input.csv`, just supply its path to the `eda_cli` command:

```bash
eda_cli input.csv
```

Or even:

```bash
eda_cli input.csv -o output.docx -c cyan --title 'EDA Report'
```

For more details on the optional arguments, pass the `-h` or `--help` flag to view the *help message*:

```bash
eda_cli -h
```

<details>

```bash
usage: eda_cli [-h] [-o OUTFILE] [-t TITLE] [-c COLOR] infile

Get a basic EDA report in docx format.

positional arguments:
  infile                A .csv or .xlsx file to process.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile OUTFILE
                        The output file (default: eda-report.docx)
  -t TITLE, --title TITLE
                        The top level heading in the report (default: Exploratory Data Analysis Report)
  -c COLOR, --color COLOR
                        A valid matplotlib color specifier (default: orangered)
```

</details>

Visit the [official documentation][docs] for more details.

[1]: https://pandas.pydata.org/
[2]: https://numpy.org/
[3]: https://matplotlib.org/
[4]: https://seaborn.pydata.org/
[5]: https://python-docx.readthedocs.io/en/latest/
[6]: https://pypi.org/project/eda_report/
[screencast]: https://raw.githubusercontent.com/Tim-Abwao/auto-eda/dev/docs/source/_static/screencast.gif
[docs]: https://eda-report.readthedocs.io/
