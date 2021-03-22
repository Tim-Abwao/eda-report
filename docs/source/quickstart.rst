Quickstart
==========

First, install ``eda_report`` using the guidelines in :doc:`installation` (if you haven't yet).

Using the Graphical User Interface
----------------------------------
This is the easiest, and the recommended way to run the application. Use the command::

    eda_report

This launches a graphical window to help you select and analyse a file.

Using the Command Line Interface
--------------------------------

You can open and analyse csv & excel files by passing their name, or path, to the ``eda_cli`` command::

    eda_cli data.csv

This processes the file, and saves the results as :file:`eda-report.docx`.

You can specify the output file's name using::

    eda_cli data.csv -o some_name.docx

Use ``eda_cli -h`` to view the *help message*, which presents all the available options.


From an Interactive Session
---------------------------

You can analyse an array-like, iterable or sequence object while in interactive mode using the function :func:`~eda_report.get_word_report`::

    >>> from eda_report import get_word_report
    >>> get_word_report(data)
