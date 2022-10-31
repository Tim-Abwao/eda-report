from collections.abc import Iterable
from typing import Union

from eda_report.document import ReportDocument
from eda_report.multivariate import MultiVariable

__version__ = "2.7.2"


def get_word_report(
    data: Iterable,
    *,
    title: str = "Exploratory Data Analysis Report",
    graph_color: str = "cyan",
    groupby_data: Union[str, int] = None,
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
        groupby_data (Union[str, int], optional): The label/index for the
            column to use to group values. Defaults to None.
        output_filename (str, optional): The name and path to save the report
            document. Defaults to "eda-report.docx".
        table_style (str, optional): The style to apply to the tables created.
            Defaults to "Table Grid".

    Returns:
        ReportDocument: Document object with analysis results.

    Example:
        .. literalinclude:: examples.txt
           :lines: 145-151

    """
    return ReportDocument(
        data,
        title=title,
        graph_color=graph_color,
        output_filename=output_filename,
        groupby_data=groupby_data,
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
           :lines: 155-212

    """
    return MultiVariable(data)
