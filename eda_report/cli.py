import argparse

from eda_report.read_file import df_from_file


def process_cli_args():
    """Captures and parses input from the command line interface.

    The `argparse`_ module from the Python standard library is used to define
    the *positional* and *optional arguments*.

    Available options are::

        usage: eda_cli [-h] [-o OUTFILE] [-t TITLE] [-c COLOR] infile

        Get a basic EDA report in docx format.

        positional arguments:
          infile                A .csv or .xlsx file to process.

        optional arguments:
          -h, --help            show this help message and exit
          -o OUTFILE, --outfile OUTFILE
                                The output file (default: eda-report.docx)
          -t TITLE, --title TITLE
                                The top level heading in the report (default:
                                Exploratory Data Analysis Report)
          -c COLOR, --color COLOR
                                A valid matplotlib color specifier (default:
                                orangered)

    .. _`argparse`: https://docs.python.org/3/library/argparse.html
    """
    parser = argparse.ArgumentParser(
        prog='eda_cli',
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

    # Set the graph color
    parser.add_argument(
        '-c', '--color', default='orangered',
        help='A valid matplotlib color specifier (default: %(default)s)')

    # Parse the arguments
    return parser.parse_args()
