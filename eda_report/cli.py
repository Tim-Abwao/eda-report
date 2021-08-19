import argparse

from eda_report.document import ReportDocument
from eda_report.gui import EDAGUI
from eda_report.read_file import df_from_file


def process_cli_args() -> argparse.Namespace:
    """Captures and parses input from the command line interface using the
    :mod:`argparse` module from the Python standard library.

    Returns
    -------
    argparse.Namespace
        A class with parsed arguments as attributes.
    """
    parser = argparse.ArgumentParser(
        prog="eda-report",
        description=(
            "Automatically analyse data and generate reports. A graphical user"
            " interface will be launched if none of the optional arguments is "
            "specified."
        ),
    )

    parser.add_argument(
        "-i",
        "--infile",
        type=df_from_file,
        help="A .csv or .xlsx file to analyse.",
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
        ),
    )

    # Parse arguments
    return parser.parse_args()


def run_from_cli():
    """Creates an exploratory data analysis report in *Word* format using input
    from the command line interface.

    This is the function executed when the package is run as a script (using
    ``python -m eda_report``). It is also the entry point for the
    ``eda-report`` command (console script).

    Running the ``eda-report`` command without any arguments launches the
    graphical user interface.

    Arguments passed from the command line are captured using the
    :func:`~eda_report.cli.process_cli_args` function, and then used to create
    a :class:`~eda_report.document.ReportDocument` object.

    Example
    --------
    .. literalinclude:: examples.txt
       :lines: 60-83
    """
    args = process_cli_args()

    if args.infile is None:
        # Launch graphical user interface to select and analyse a file
        app = EDAGUI()
        app.mainloop()

    else:
        return ReportDocument(
            args.infile,
            title=args.title,
            graph_color=args.color,
            output_filename=args.outfile,
            target_variable=args.target,
        )
