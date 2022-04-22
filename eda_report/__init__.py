from collections.abc import Iterable
from typing import Union

from eda_report.document import ReportDocument
from eda_report.multivariate import MultiVariable

__version__ = "2.5.0"


def get_word_report(
    data: Iterable,
    *,
    title: str = "Exploratory Data Analysis Report",
    graph_color: str = "cyan",
    target_variable: Union[str, int] = None,
    output_filename: str = "eda-report.docx",
    table_style: str = "Table Grid",
) -> ReportDocument:
    """Analyzes data, and generates a report in *Word* (*.docx*) format.

    Args:
        data (Iterable): The data to analyze.
        title (str, optional): The title to assign the report. Defaults to
            "Exploratory Data Analysis Report".
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        target_variable (Union[str, int], optional): The label/index for the
            column to use to group values. Defaults to None.
        output_filename (str, optional): The name and location to save the
         report document. Defaults to "eda-report.docx".
        table_style (str, optional): The style to apply to the tables created.
            Defaults to "Table Grid".

    Returns:
        ReportDocument: Document object with analysis results.

    Example:
        .. literalinclude:: examples.txt
           :lines: 148-155

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
        data (Iterable): The data to analyze.

    Returns:
        MultiVariable: Analysis results.

    Examples:
        .. literalinclude:: examples.txt
           :lines: 159-217

    """
    return MultiVariable(data)
