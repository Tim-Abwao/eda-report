from eda_report.cli import process_cli_args
from eda_report.document import ReportDocument

__version__ = "1.4.0b"


def get_word_report(
    data,
    *,
    title="Exploratory Data Analysis Report",
    graph_color="orangered",
    output_filename="eda-report.docx",
    target_variable=None
):
    """Analyses the input data, and generates a report in *.docx* format.

    This is simply a wrapper around the
    :class:`~eda_report.document.ReportDocument` object, and the arguments
    supplied are passed to it.

    :param data: The data to analyse.
    :type data: an array-like or sequence.
    :param title: The top level heading for the generated report, defaults to
        'Exploratory Data Analysis Report'.
    :type title: str, optional
    :param graph_color: The color to apply to the generated graphs, defaults
        to 'orangered'. See the *matplotlib* `list of named colors`_ for all
        available options.
    :type graph_color: str, optional
    :param output_filename: The name and path to use in saving the generated
        report file, defaults to 'eda-report.docx' in the current directory.
    :type output_filename: str, optional
    :param target_variable: The target variable (dependent feature). An
            *integer value* is treated as a *column index*, whereas a *string*
            is treated as a *column label*.
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


def run_from_cli():
    """Creates an exploratory data analysis report in *.docx* format using input
    from the command line interface.

    This is the function executed when the package is run as a script (using
    ``python -m eda_report``. It is also the entry point for the ``eda_cli``
    console script (command).

    Arguments passed from the command line are captured using the
    :func:`~eda_report.cli.process_cli_args` function, and then supplied to the
    :func:`~eda_report.get_word_report` function to generate the report.
    """
    # Collect parameters from the command line interface
    args = process_cli_args()
    # Generate a report
    get_word_report(
        args.infile,
        title=args.title,
        graph_color=args.color,
        output_filename=args.outfile,
        target_variable=args.target,
    )
