from eda_report.cli import process_cli_args
from eda_report.document import ReportDocument

__version__ = '1.2.0'


def get_word_report(data, *, title='Exploratory Data Analysis Report',
                    graph_color='orangered',
                    output_filename='eda-report.docx'):
    """Analyses the input data, and generates a report in *.docx* format.

    The is simply a wrapper around the
    :class:`~eda_report.document.ReportDocument` object.

    :param data: The data to analyse.
    :type data: ``pandas.DataFrame``, ``pandas.Series``, an array-like or
        sequence.
    :param title: The top level heading for the generated report, defaults to
        'Exploratory Data Analysis Report'.
    :type title: str, optional
    :param graph_color: The color to apply to the generated graphs, defaults
        to 'orangered'. Any valid matplotlib color specifier will do.
    :type graph_color: str, optional
    :param output_filename: The name to give the generated report file,
        defaults to 'basic-report.docx'.
    :type output_filename: str, optional
    """
    ReportDocument(data, title=title, graph_color=graph_color,
                   output_filename=output_filename)


def run_from_cli():
    """Creates an exploratory data analysis report in *.docx* format using input
    from the command line interface.

    Arguments passed from the command line are parsed using the
    :func:`~eda_report.cli.process_cli_args` function, and then supplied to the
    :func:`~eda_report.get_word_report` function to generate the report.
    """
    args = process_cli_args()
    get_word_report(args.infile, title=args.title, graph_color=args.color,
                    output_filename=args.outfile)
