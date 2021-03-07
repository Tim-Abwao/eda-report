``eda_report`` User Guide
=========================

Simplify the `exploratory data analysis`_ and reporting process. ``eda_report``:

#. Automatically analyses a dataset using `pandas`_' built-in methods. 
      Summary statistics for both numeric and categorical variables are computed and packaged as tables.
#. Plots visualisations using `matplotlib`_ and `seaborn`_.
      Box-plots, histograms and scatter-plots for numeric variables. Bar-plots for categorical variables.
#. Generates a basic report in .docx format using `python-docx`_.
      The report gives a brief summary of the characteristics of the dataset, then gives details (summary statistics & plots) for each variable. It ends with pair-wise comparisons(scatterplots & correlation) for all present numerical variables.

.. tip::
      For a more comprehensive report, in HTML format, consider using `pandas_profiling`_.

.. _exploratory data analysis: https://en.wikipedia.org/wiki/Exploratory_data_analysis
.. _pandas: https://pandas.pydata.org/
.. _matplotlib: https://matplotlib.org/
.. _seaborn: https://seaborn.pydata.org/
.. _python-docx: https://python-docx.readthedocs.io/en/latest/
.. _pandas_profiling: https://pandas-profiling.github.io/pandas-profiling/docs/master/index.html

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   eda_report

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
