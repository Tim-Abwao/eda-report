from collections.abc import Iterable
from typing import Union

from eda_report._validate import _validate_dataset
from eda_report.bivariate import Dataset
from eda_report.document import ReportDocument
from eda_report.univariate import Variable

__version__ = "2.8.1"


def get_word_report(
    data: Iterable,
    *,
    title: str = "Exploratory Data Analysis Report",
    graph_color: str = "cyan",
    groupby_variable: Union[str, int] = None,
    output_filename: str = "eda-report.docx",
    table_style: str = "Table Grid",
) -> ReportDocument:
    """Analyze `data`, and generate a report document in *Word* (*.docx*)
    format.

    Args:
        data (Iterable): The data to analyze.
        title (str, optional): The title to assign the report. Defaults to
            "Exploratory Data Analysis Report".
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        groupby_variable (Union[str, int], optional): The label/index for the
            column to use to group values. Defaults to None.
        output_filename (str, optional): The name/path to save the report
            document. Defaults to "eda-report.docx".
        table_style (str, optional): The style to apply to the tables created.
            Defaults to "Table Grid".

    Returns:
        ReportDocument: Document object with analysis results.

    Example:
        .. literalinclude:: examples.txt
           :lines: 136-142
    """
    return ReportDocument(
        data,
        title=title,
        graph_color=graph_color,
        output_filename=output_filename,
        groupby_variable=groupby_variable,
        table_style=table_style,
    )


def summarize(data: Iterable) -> Union[Variable, Dataset]:
    """Get summary statistics for the supplied data.

    Args:
        data (Iterable): The data to analyze.

    Returns:
        Union[Variable, Dataset]: Analysis results.

    Example:
        .. literalinclude:: examples.txt
           :lines: 172-195
    """
    data = _validate_dataset(data)
    if data.shape[1] == 1:
        return Variable(data.squeeze())
    else:
        return Dataset(data)
