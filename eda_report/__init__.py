from typing import Optional, Union
from collections.abc import Iterable
from eda_report.document import ReportDocument


__version__ = "2.0.0rc0"


def get_word_report(
    data: Iterable,
    *,
    title: str = "Exploratory Data Analysis Report",
    graph_color: str = "cyan",
    target_variable: Optional[Union[str, int]] = None,
    output_filename: str = "eda-report.docx",
    table_style: str = "Table Grid",
) -> ReportDocument:
    """Analyses input data, and generates a report in *Word* (*.docx*) format.

    This is simply a wrapper around the
    :class:`~eda_report.document.ReportDocument` object, and the arguments
    supplied are passed to it.

    Parameters
    ----------
    data : Iterable
        The data to analyse.
    target_variable : Optional[Union[str, int]]
        The column
    title : str, optional
        The title to assign the report, by default "Exploratory Data Analysis
        Report"
    graph_color : str, optional
        The color to apply to the graphs, by default "cyan"
    output_filename : str, optional
        The file name or path to save the document to, by default
        "eda-report.docx"
    table_style : str, optional
        The style to apply to the tables created, by default "Table Grid"

    Returns
    -------
    ReportDocument
        The report object.
    """
    return ReportDocument(
        data,
        title=title,
        graph_color=graph_color,
        output_filename=output_filename,
        target_variable=target_variable,
        table_style=table_style
    )
