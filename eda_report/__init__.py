from eda_report.cli import process_cli_args
from eda_report.document import ReportDocument

__version__ = '1.3.1'


def get_word_report(data, *, title='Exploratory Data Analysis Report',
                    graph_color='orangered',
                    output_filename='eda-report.docx'):
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

    .. _`list of named colors`:
        https://matplotlib.org/stable/gallery/color/named_colors.html
    """
    ReportDocument(data, title=title, graph_color=graph_color,
                   output_filename=output_filename)


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
    args = process_cli_args()
    get_word_report(args.infile, title=args.title, graph_color=args.color,
                    output_filename=args.outfile)
