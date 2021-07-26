import argparse

from eda_report.document import ReportDocument
from eda_report.read_file import df_from_file


def process_cli_args(*args) -> argparse.Namespace:
    """Captures and parses input from the command line interface using the
    :mod:`argparse` module from the Python standard library.

    Returns
    -------
    argparse.Namespace
        A class with parsed arguments as attributes.
    """
    parser = argparse.ArgumentParser(
        prog="eda_cli",
        description="Automatically analyse data and generate reports.",
    )

    parser.add_argument(
        "infile", type=df_from_file, help="A .csv or .xlsx file to analyse."
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
        "-T",
        "--target",
        help=(
            "The target variable (dependent feature), used to color-code "
            "plotted values. An integer value is treated as a column index, "
            "whereas a string is treated as a column label."
            " (Default: %(default)s)"
        ),
    )

    # Parse arguments
    if args:
        return parser.parse_args(args)
    else:
        return parser.parse_args()


def run_from_cli():  # pragma: no cover
    """Creates an exploratory data analysis report in *Word* format using input
    from the command line interface.

    This is the function executed when the package is run as a script (using
    ``python -m eda_report``. It is also the entry point for the ``eda_cli``
    console script (command).

    Arguments passed from the command line are captured using the
    :func:`~eda_report.cli.process_cli_args` function, and then supplied to the
    :class:`~eda_report.document.ReportDocument` object to generate the report.
    """
    args = process_cli_args()

    ReportDocument(
        args.infile,
        title=args.title,
        graph_color=args.color,
        output_filename=args.outfile,
        target_variable=args.target,
    )
