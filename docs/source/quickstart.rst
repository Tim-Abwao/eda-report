Quickstart
==========

Using the Graphical User Interface
----------------------------------

The command ``eda-report`` launches a graphical window to help select a *csv* or *excel* file to analyze::

    $ eda-report

.. figure:: _static/screencast.*
   :alt: an image of the graphical user interface

   A ``tkinter``-based graphical user interface to the application

You will be prompted to enter your desired *title*, *groupby/target variable*, *graph color* & *output file-name*. Afterwards, a report is generated, as specified, from the contents of the selected file.

.. hint::
    For help with `Tk` - related issues, consider visiting `TkDocs`_.

.. _`TkDocs`: https://tkdocs.com/index.html

Using the Command Line Interface
--------------------------------

You can specify an input file and an output file-name::

    $ eda-report -i data.csv -o some_name.docx

.. literalinclude:: examples.txt
       :lines: 105-127

From an Interactive Session
---------------------------

You can use the :func:`~eda_report.get_word_report` function to generate reports:

.. literalinclude:: examples.txt
   :lines: 135-141

You can use the :func:`~eda_report.summarize` function to analyze datasets:

.. literalinclude:: examples.txt
   :lines: 145-194

You can plot several statistical graphs (see :ref:`plotting-examples`):

>>> import eda_report.plotting as ep
>>> ax = ep.plot_correlation(mpg_data)
>>> ax.figure.savefig("correlation-plot.png")

.. image:: _static/correlation-plot.png
   :width: 80%
   :align: center
   :alt: a correlation-plot
   :class: only-light

.. image:: _static/correlation-plot-dark.png
   :width: 80%
   :align: center
   :alt: a correlation-plot
   :class: only-dark
