``eda_report`` User Guide
=========================

Simplify the `exploratory data analysis`_ and reporting process:

#. Automatically analyse a dataset. 
      Input data is processed using `pandas`_' built-in methods. *Summary statistics* for both **numeric** and **categorical** variables are computed and packaged as tables.
#. Get revealing visualisations.
      *Box-plots*, *histograms*, *probability-plots*, *run-plots* and *scatter-plots* for numeric variables; *bar-plots* for categorical variables. Created with `matplotlib`_ and `seaborn`_.
#. Generate a report in *.docx* format.
      An overview of the characteristics of the input data; summary statistics & plots for each variable; and pair-wise comparisons for all numerical variables present. Produced with `python-docx`_. You can afterwards easily edit the report to your liking.

.. _exploratory data analysis: https://en.wikipedia.org/wiki/Exploratory_data_analysis
.. _pandas: https://pandas.pydata.org/
.. _matplotlib: https://matplotlib.org/
.. _seaborn: https://seaborn.pydata.org/
.. _python-docx: https://python-docx.readthedocs.io/en/latest/

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
