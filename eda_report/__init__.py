from eda_report.document import ReportDocument
from eda_report.cli import process_cli_args

__version__ = '0.0.6'


def get_word_report(data, *, title='Exploratory Data Analysis Report',
                    graph_colour='orangered',
                    output_filename='eda-report.docx'):
    """Analyse the data, and generate a report in .docx format.

    :param data: The data to analyse.
    :type data: :class:`pandas.DataFrame`, :class:`pandas.Series`, an array or
        sequence.
    :param title: The top level heading for the generated report, defaults to
        'Exploratory Data Analysis Report'.
    :type title: str, optional
    :param graph_colour: The colour to apply to the generated graphs. Any
        valid matplotlib colors specifier, defaults to 'orangered'.
    :type graph_colour: str, optional
    :param output_filename: The name to give the generated report file,
        defaults to 'basic-report.docx'.
    :type output_filename: str, optional
    """
    ReportDocument(data, title=title, graph_colour=graph_colour,
                   output_filename=output_filename)


def run_from_cli():
    """Create an EDA report using arguments from the command line.
    """
    args = process_cli_args()
    get_word_report(args.infile, title=args.title, graph_colour=args.colour,
                    output_filename=args.outfile)
