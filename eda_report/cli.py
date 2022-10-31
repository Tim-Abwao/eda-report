import argparse
from typing import Optional

from eda_report.document import ReportDocument
from eda_report.read_file import df_from_file


def process_cli_args() -> argparse.Namespace:
    """Captures and parses input from the command line interface using the
    :mod:`argparse` module from the Python standard library.

    Returns:
        argparse.Namespace: Object with the parsed arguments as attributes.

    Example:
        .. literalinclude:: examples.txt
           :lines: 115-137
    """
    parser = argparse.ArgumentParser(
        prog="eda-report",
        description=(
            "Automatically analyze data and generate reports. A graphical user"
            " interface will be launched if none of the optional arguments is "
            "specified."
        ),
    )

    parser.add_argument(
        "-i",
        "--infile",
        type=df_from_file,
        help="A .csv or .xlsx file to analyze.",
    )

    parser.add_argument(
        "-o",
        "--outfile",
        default="eda-report.docx",
        help="The output name for analysis results (default: %(default)s)",
    )

    parser.add_argument(
        "-t",
        "--title",
        default="Exploratory Data Analysis Report",
        help="The top level heading for the report (default: %(default)s)",
    )

    parser.add_argument(
        "-c",
        "--color",
        default="cyan",
        help="The color to apply to graphs (default: %(default)s)",
    )

    parser.add_argument(
        "-g",
        "-T",
        "--groupby",
        "--target",
        help=(
            "The variable to use for grouping plotted values. An integer value"
            " is treated as a column index, whereas a string is treated as a"
            " column label."
        ),
    )

    return parser.parse_args()


def run_from_cli() -> Optional[ReportDocument]:
    """Creates an exploratory data analysis report in *Word* format using input
    from the command line interface.

    This is the function executed when the package is run as a script (using
    ``python -m eda_report``). It is also the entry point for the
    ``eda-report`` command (console script).
    """
    args = process_cli_args()

    if args.infile is None:
        from eda_report.gui import EDAGUI

        # Launch graphical user interface to select and analyze a file
        app = EDAGUI()
        app.mainloop()

    else:
        ReportDocument(
            args.infile,
            title=args.title,
            graph_color=args.color,
            output_filename=args.outfile,
            groupby_data=args.groupby,
        )
