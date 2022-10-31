``eda-report`` User Guide
=========================

Speed up the `exploratory data analysis`_ and reporting process. Automatically analyze a dataset, and get:

1. Statistical properties
-------------------------

Descriptive statistics, bivariate analysis, tests for normality and more:

.. literalinclude:: examples.txt
   :lines: 155-156, 159-212

2. Revealing visualizations
---------------------------

- *Box-plots*, *kde-plots*, *normal-probability-plots*, *scatter-plots* and a *correlation bar-chart* for numeric variables.
- *Bar-plots* for categorical variables.

>>> import eda_report.plotting as ep
>>> fig = ep.regression_plot(mpg_data["acceleration"], mpg_data["horsepower"],
...                          labels=("Acceleration", "Horsepower"))
>>> fig.savefig("regression-plot.png")

.. image:: _static/regression-plot.png
   :width: 80%
   :align: center
   :alt: a regression-plot
   :class: only-light

.. image:: _static/regression-plot-dark.png
   :width: 80%
   :align: center
   :alt: a regression-plot
   :class: only-dark

3. A report in *Word* (.docx) format
------------------------------------

An exploratory data analysis report document complete with variable descriptions, summary statistics, statistical plots, contingency tables and more:

.. literalinclude:: examples.txt
         :lines: 145-151

.. figure:: _static/report.*
   :alt: iris dataset report animation

   A report generated from the *iris dataset*.

.. image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/Tim-Abwao/eda-report/HEAD?filepath=eda-report-basics.ipynb

.. _exploratory data analysis: https://en.wikipedia.org/wiki/Exploratory_data_analysis


Installation
------------

.. important::
    Only **Python3.8 to 3.10** are currently supported.

.. hint::
   Consider using a `virtual environment`_. Virtual environments are a great way to ensure that you install the right versions of dependencies, while avoiding breaking other Python packages in your system.

You can install ``eda-report`` from the `Python Package Index`_ using ``pip``::

    $ pip install eda-report

You can also install the latest stable version right from the `GitHub repository`_ using::

    $ pip install https://github.com/tim-abwao/eda-report/archive/main.tar.gz


.. _virtual environment: https://docs.python.org/3/tutorial/venv.html#virtual-environments-and-packages
.. _Python Package Index: https://pypi.org/project/eda-report/
.. _GitHub repository: https://github.com/Tim-Abwao/eda-report

.. toctree::
   :maxdepth: 2

   quickstart
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
