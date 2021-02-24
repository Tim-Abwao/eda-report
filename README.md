# Basic Exploratory Data Analysis Report

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Tim-Abwao/auto-eda/master)
[![PyPI version](https://badge.fury.io/py/eda-report.svg)](https://badge.fury.io/py/eda-report)

A simple Python program to help automate EDA report generation.

The data is analysed using [pandas][1]' built in methods, and graphs are plotted using [matplotlib][3] & [seaborn][4]. The results are then packaged as a *Word .docx* file using [python-docx][5].

## Installation

You can install the package from [PyPI][6] using:

```bash
pip install eda-report
```

## Basic usage

```python
>>> import eda_report
>>> eda_report.get_word_report(df)
```

where `df` is a pandas `DataFrame`.

[1]: https://pandas.pydata.org/
[2]: https://numpy.org/
[3]: https://matplotlib.org/
[4]: https://seaborn.pydata.org/
[5]: https://python-docx.readthedocs.io/en/latest/
[6]: https://pypi.org/project/eda_report/
