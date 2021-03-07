import argparse
from eda_report.read_file import df_from_file


def process_cli_args():
    """This function creates the positional and optional arguments for the
    command line interface, and also parses input from the command line.

    It uses the `argparse`_ module from the Python standard library.

    .. _`argparse`: https://docs.python.org/3/library/argparse.html
    """
    parser = argparse.ArgumentParser(
        prog='eda_report',
        description='Get a basic EDA report in docx format.')

    # Get the data from a file
    parser.add_argument(
        'infile', type=df_from_file,
        help='A .csv or .xlsx file to process.')

    # Set the output file's name
    parser.add_argument(
        '-o', '--outfile', default='eda-report.docx',
        help='The output file (default: %(default)s)')

    # Set the report's title
    parser.add_argument(
        '-t', '--title', default='Exploratory Data Analysis Report',
        help='The top level heading in the report (default: %(default)s)')

    # Set the graph colour
    parser.add_argument(
        '-c', '--colour', default='orangered',
        help='A valid matplotlib color specifier (default: %(default)s)')

    # Parse the arguments
    return parser.parse_args()
