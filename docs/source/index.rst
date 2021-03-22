``eda_report`` User Guide
=========================

Simplify the `exploratory data analysis`_ and reporting process:

#. Automatically analyse a dataset. 
      Input data is processed using `pandas`_' built-in methods. *Summary statistics* for both **numeric** and **categorical** variables are computed and packaged as tables.
#. Get revealing visualisations.
      Box-plots, histograms and scatter-plots for numeric variables; bar-plots for categorical variables. Produced using `matplotlib`_ and `seaborn`_.
#. Generate a report in *.docx* format.
      The report gives a brief summary of the characteristics of the input data, then gives details (summary statistics & plots) for each variable. It ends with pair-wise comparisons(scatterplots & correlation) for all present numerical variables. It is created using `python-docx`_, and you can afterwards easily edit it to your liking.

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
