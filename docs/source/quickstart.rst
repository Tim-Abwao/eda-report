Quickstart
==========

Using the Graphical User Interface
----------------------------------

The command ``eda-report`` launches a graphical window to help you select a *csv* or *excel* file to analyse::

    $ eda-report

.. figure:: _static/screencast.*
   :alt: an image of the graphical user interface

   A ``tkinter``-based graphical user interface to the application

You will be prompted to enter your desired *title*, *target variable*, *graph color* & *output file-name*. Then a report document will be generated, as specified, from the contents of the selected file.


.. hint::
    For help with `Tk` - related issues, consider visiting `TkDocs`_.

.. _`TkDocs`: https://tkdocs.com/index.html

Using the Command Line Interface
--------------------------------

You can specify the input file and an output file-name with::

    $ eda-report -i data.csv -o some_name.docx

.. literalinclude:: examples.txt
       :lines: 3-26

From an Interactive Session
---------------------------

You can use the :func:`~eda_report.summarize` function to analyse datasets. It returns a :class:`~eda_report.multivariate.MultiVariable` object:

.. literalinclude:: examples.txt
       :lines: 30-59

You can use the :func:`~eda_report.get_word_report` function to generate reports:

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
   :lines: 63-83
