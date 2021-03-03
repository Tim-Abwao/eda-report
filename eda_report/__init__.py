from eda_report.document import ReportDocument
from eda_report.cli import process_cli_args

__version__ = '0.0.4'


def get_word_report(data, *, title='Exploratory Data Analysis Report',
                    graph_colour='orangered',
                    output_filename='basic-report.docx'):
    """Get an EDA report in .docx format."""
    ReportDocument(data, title=title, graph_colour=graph_colour,
                   output_filename=output_filename)


def run_from_cli():
    """Create the report using arguments from the command line."""
    args = process_cli_args()
    get_word_report(args.infile, title=args.title, graph_colour=args.colour,
                    output_filename=args.outfile)
