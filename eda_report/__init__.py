from collections.abc import Iterable
from typing import Optional, Union

from eda_report.document import ReportDocument
from eda_report.multivariate import MultiVariable

__version__ = "2.4.1"


def get_word_report(
    data: Iterable,
    *,
    title: str = "Exploratory Data Analysis Report",
    graph_color: str = "cyan",
    target_variable: Optional[Union[str, int]] = None,
    output_filename: str = "eda-report.docx",
    table_style: str = "Table Grid",
) -> ReportDocument:
    """Analyses data, and generates a report in *Word* (*.docx*) format.

    Args:
        data (Iterable): The data to analyse.
        title (str, optional): The title to assign the report. Defaults to
            "Exploratory Data Analysis Report".
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        target_variable (Optional[Union[str, int]], optional): The column to
            use to group values. Defaults to None.
        output_filename (str, optional): The file name or path to save the
            document to. Defaults to "eda-report.docx".
        table_style (str, optional): The style to apply to the tables created.
            Defaults to "Table Grid".

    Returns:
        ReportDocument: Document with analysis results.

    Example:
        .. literalinclude:: examples.txt
           :lines: 148-154

    """
    return ReportDocument(
        data,
        title=title,
        graph_color=graph_color,
        output_filename=output_filename,
        target_variable=target_variable,
        table_style=table_style,
    )


def summarize(data: Iterable) -> MultiVariable:
    """Get summary statistics for the supplied data.

    Args:
        data (Iterable): The data to analyse.

    Returns:
        MultiVariable: Analysis results.

    Examples:
        .. literalinclude:: examples.txt
           :lines: 159-217

    """
    return MultiVariable(data)
