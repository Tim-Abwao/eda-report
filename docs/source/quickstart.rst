Quickstart
==========

First, install ``eda_report`` using the guidelines in :doc:`installation` (if you haven't yet).

Using the Graphical User Interface
----------------------------------
This is the easiest, and the recommended way to run the application. Use the command::

    eda_report

This launches a graphical window to help you select a file to analyse .

.. figure:: _static/gui.png
   :alt: an image of the graphical user interface

   A ``tkinter``-based graphical user interface to the application

You will be prompted to configure some options (*report title*, *graph color* & *output file-name*), and a report document will be generated, as specified, from the contents of the selected file.

Using the Command Line Interface
--------------------------------

You can open and analyse **csv** & **excel** files by passing their name, or path, to the ``eda_cli`` command.

To process the file ``data.csv``, and save the results as ``eda-report.docx`` (*default*), use::
    
    eda_cli data.csv

You can specify the output file's name and location using the ``-o`` option::

    eda_cli data.csv -o some_name.docx

Use ``eda_cli -h`` to display the *help message* with all available options.


From an Interactive Session
---------------------------

You can analyse an *array-like*, *iterable* or *sequence-like* object while in interactive mode using the function :func:`~eda_report.get_word_report`::

    >>> from eda_report import get_word_report
    >>> get_word_report(data)

The result is a exploratory data analysis report document in *.docx* format.

You can also use the :class:`~eda_report.univariate.Variable` and :class:`~eda_report.multivariate.MultiVariable` classes to analyse data::

    >>> x = Variable(data=range(50))
    >>> x.statistics
    Number of observations    50.00000
    Average                   24.50000
    Standard Deviation        14.57738
    Minimum                    0.00000
    Lower Quartile            12.25000
    Median                    24.50000
    Upper Quartile            36.75000
    Maximum                   49.00000
    Skewness                   0.00000
    Kurtosis                  -1.20000
    dtype: float64
    >>> x.show_graphs()
