Quickstart
==========

Using the Graphical User Interface
----------------------------------

The command ``eda_report`` launches a graphical window to help you select a *csv* or *excel* file to analyse::

    $ eda_report

.. figure:: _static/screencast.*
   :alt: an image of the graphical user interface

   A ``tkinter``-based graphical user interface to the application

You will be prompted to enter your desired *title*, *target variable*, *graph color* & *output file-name*. Then a report document will be generated, as specified, from the contents of the selected file.

From an Interactive Session
---------------------------

You can use the :func:`~eda_report.get_word_report` function generates reports:

>>> from eda_report import get_word_report
>>> from seaborn import load_dataset
>>> data = load_dataset("iris")
>>> get_word_report(data)
Bivariate analysis: 100%|███████████████████████████████████| 6/6 numeric pairs.
Univariate analysis: 100%|███████████████████████████████████| 5/5 features.
[INFO 14:34:55.686] Done. Results saved as 'eda-report.docx'
<eda_report.document.ReportDocument object at 0x7f23acf2fd00>

You can analyse a one-dimensional dataset using the :class:`~eda_report.univariate.Variable` object:

.. literalinclude:: examples.txt
   :lines: 3-23

You can analyse a multivariate dataset using the :class:`~eda_report.multivariate.MultiVariable` object:

.. literalinclude:: examples.txt
   :lines: 28-58

Using the Command Line Interface
--------------------------------

The command ``eda_cli`` takes input from the command-line. You can analyse *csv* or *excel* files by supplying their path. For instance, to process a file named ``data.csv`` in the current directory, use::
    
    $ eda_cli data.csv

You can specify the output file-name and location using the ``-o`` option::

    $ eda_cli data.csv -o some_name.docx

Use ``eda_cli -h`` to view all available options.
