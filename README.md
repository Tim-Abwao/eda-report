# Basic Exploratory Data Analysis Report

A Jupyter notebook to help automate EDA report generation.

The data is analysed using [pandas][1] & [numpy][2], plotted using [matplotlib][3] & [seaborn][4], and then packaged as a *Word .docx* file using [python-docx][5].

## Running locally

1. Download the files, and create a new virtual environment:

    ```bash
    git clone https://github.com/Tim-Abwao/auto-eda
    cd auto-eda
    python3 -m venv venv
    source venv/bin/activate
    ```

2. Install the required packages, and launch the Jupyter server:

    ```bash
    pip install -U pip
    pip install -r requirements.txt
    jupyter notebook 'Basic EDA Report.ipynb'
    ```

[1]: https://pandas.pydata.org/
[2]: https://numpy.org/
[3]: https://matplotlib.org/
[4]: https://seaborn.pydata.org/
[5]: https://python-docx.readthedocs.io/en/latest/
