from pandas import DataFrame

from eda_report import get_word_report, summarize
from eda_report.bivariate import Dataset
from eda_report.document import ReportDocument
from eda_report.univariate import Variable

sample_data = DataFrame(
    {
        "A": range(50),
        "B": list("abcdef") * 8 + ["a"] * 2,
        "C": [True, False] * 24 + [True] * 2,
        "D": [1, 3, 5, 7, 9, 11, 13] * 7 + [17],
    }
)


def test_get_word_report_function():
    report = get_word_report(sample_data)
    assert isinstance(report, ReportDocument)


def test_summarize_function():
    summary_1D = summarize(range(25))
    assert isinstance(summary_1D, Variable)

    summary_2D = summarize(sample_data)
    assert isinstance(summary_2D, Dataset)
