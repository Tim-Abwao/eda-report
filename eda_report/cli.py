import argparse

from eda_report.read_file import df_from_file


def process_cli_args(*args):
    """Captures and parses input from the command line interface using the
    :mod:`argparse` module from the Python standard library.

    Available options are::

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
          -T TARGET, --target TARGET
                                The target variable (dependent feature), used
                                to color-code plotted values. An integer value
                                is treated as a column index, whereas a string
                                is treated as a column label. (Default: None)
    """
    parser = argparse.ArgumentParser(
        prog="eda_cli", description="Get a basic EDA report in docx format."
    )

    # Get the data from a file
    parser.add_argument(
        "infile", type=df_from_file, help="A .csv or .xlsx file to process."
    )

    # Set the output file's name
    parser.add_argument(
        "-o",
        "--outfile",
        default="eda-report.docx",
        help="The output file (default: %(default)s)",
    )

    # Set the report's title
    parser.add_argument(
        "-t",
        "--title",
        default="Exploratory Data Analysis Report",
        help="The top level heading in the report (default: %(default)s)",
    )

    # Set the graph color
    parser.add_argument(
        "-c",
        "--color",
        default="orangered",
        help="A valid matplotlib color specifier (default: %(default)s)",
    )

    # Set the target variable
    parser.add_argument(
        "-T",
        "--target",
        help=(
            "The target variable (dependent feature), used to color-code "
            "plotted values. An integer value is treated as a column index, "
            "whereas a string is treated as a column label."
            " (Default: %(default)s)"
        ),
    )

    # Parse the arguments
    if args:
        return parser.parse_args(args)
    else:
        return parser.parse_args()
