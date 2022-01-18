from collections.abc import Iterable
from typing import Optional, Union

from eda_report.document import ReportDocument
from eda_report.multivariate import MultiVariable

__version__ = "2.3.0"


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
    :class:`~eda_report.document.ReportDocument` class, and the arguments
    supplied are passed to it.

    Parameters
    ----------
    data : Iterable
        The data to analyse.
    target_variable : Optional[Union[str, int]]
        The column to use to group values and color-code graphs.
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

    Example
    --------
    >>> eda_report.get_word_report([[1, 2], [3, 4]])
    Bivariate analysis: 100%|█████████████████████████████| 1/1 numeric pairs.
    Univariate analysis: 100%|█████████████████████████████████| 2/2 features.
    [INFO 00:16:16.821] Done. Results saved as 'eda-report.docx'
    <eda_report.document.ReportDocument object at 0x7fc3f7efaa90>
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
    """Get a statistical summary of the supplied dataset.

    Parameters
    ----------
    data : Iterable
        The data to analyse.

    Returns
    -------
    MultiVariable
        Analysis results, with components as attributes.

    Example
    -------
    .. literalinclude:: examples.txt
       :lines: 85-113
    """
    return MultiVariable(data)
