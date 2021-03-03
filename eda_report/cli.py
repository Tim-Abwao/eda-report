import argparse
from eda_report.read_file import df_from_file


def process_cli_args():
    """Process command line arguments to analyse a file."""
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


if __name__ == '__main__':
    process_cli_args()
