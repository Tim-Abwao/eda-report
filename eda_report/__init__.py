from eda_report.cli import process_cli_args
from eda_report.document import ReportDocument
from eda_report.gui import EDAGUI

__version__ = "1.6.1"


def get_word_report(
    data,
    *,
    title="Exploratory Data Analysis Report",
    graph_color="orangered",
    output_filename="eda-report.docx",
    target_variable=None
):
    """Analyses input data, and generates a report in *Word* (*.docx*) format.

    This is simply a wrapper around the
    :class:`~eda_report.document.ReportDocument` object, and the arguments
    supplied are passed to it.

    :param data: The data to analyse.
    :type data: array-like, sequence, iterable.
    :param title: The top level heading for the generated report, defaults to
        'Exploratory Data Analysis Report'.
    :type title: str, optional
    :param graph_color: The color to apply to the generated graphs, defaults
        to 'orangered'. See the *matplotlib* `list of named colors`_ for all
        available options.
    :type graph_color: str, optional
    :param output_filename: The name and path for the generated report file,
        defaults to 'eda-report.docx'.
    :type output_filename: str, optional
    :param target_variable: The dependent feature. Used to color-code plotted
        values. An *integer value* is treated as a *column index*, whereas a
        *string* is treated as a *column label*.
    :type target_variable: int, str, optional

    .. _`list of named colors`:
        https://matplotlib.org/stable/gallery/color/named_colors.html
    """
    # Generate a report using the supplied parameters
    ReportDocument(
        data,
        title=title,
        graph_color=graph_color,
        output_filename=output_filename,
        target_variable=target_variable,
    )


def run_from_cli():  # pragma: no cover
    """Creates an exploratory data analysis report in *Word* format using input
    from the command line interface.

    This is the function executed when the package is run as a script (using
    ``python -m eda_report``. It is also the entry point for the ``eda_cli``
    console script (command).

    Arguments passed from the command line are captured using the
    :func:`~eda_report.cli.process_cli_args` function, and then supplied to the
    :class:`~eda_report.document.ReportDocument` object to generate the report.
    """
    # Collect parameters from the command line interface
    args = process_cli_args()
    # Generate a report
    ReportDocument(
        args.infile,
        title=args.title,
        graph_color=args.color,
        output_filename=args.outfile,
        target_variable=args.target,
    )


def run_in_gui():  # pragma: no cover
    """Starts the *graphical user interface* to the application.

    This provides the entry point for the ``eda_report`` console script
    (command).
    """
    app = EDAGUI()
    app.mainloop()
