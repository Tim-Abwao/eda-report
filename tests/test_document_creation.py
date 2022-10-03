from io import BytesIO

from eda_report import get_word_report
from eda_report.document import ReportDocument
from pandas.core.frame import DataFrame


class TestReportWithIdealInput:

    data = DataFrame(
        {"A": range(50), "B": [1, 2, 3, 4, 5] * 10, "C": list("ab") * 25}
    )
    report = get_word_report(
        data,
        title="Test Report",
        graph_color="teal",
        groupby_data="C",
        output_filename=BytesIO(),
    )

    def test_general_properties(self):
        # Largely covered in ReportContent tests
        assert self.report.TITLE == "Test Report"
        assert self.report.GRAPH_COLOR == "teal"
        assert "correlation_heatmap" in self.report.bivariate_graphs
        assert "regression_plots" in self.report.bivariate_graphs
        assert self.report.TABLE_STYLE == "Table Grid"


class TestReportWithLimitedInput:

    data = DataFrame(
        {"categorical": list("ABCDEFGHIJKL" * 2), "numeric": range(24)}
    )
    report = get_word_report(
        data,
        title="One Numeric One Categorical",
        graph_color="lime",
        output_filename=BytesIO(),
    )

    def test_report_creation(self):
        assert isinstance(self.report, ReportDocument)
        assert self.report.TITLE == "One Numeric One Categorical"
        assert self.report.GRAPH_COLOR == "lime"
        assert list(self.report.variable_info.keys()) == [
            "categorical",
            "numeric",
        ]

    def test_bivariate_analysis(self):
        assert self.report.bivariate_summaries is None
        assert self.report.bivariate_graphs is None


class TestReportWithUnivariateInput:

    univariate_numeric_report = get_word_report(
        DataFrame(range(5)),
        title="Univariate Numeric Report",
        output_filename=BytesIO(),
    )
    univariate_categorical_report = get_word_report(
        DataFrame(["a"]),
        title="Univariate Categorical Report",
        output_filename=BytesIO(),
    )

    def test_bivariate_analysis(self):
        assert self.univariate_numeric_report.bivariate_summaries is None
        assert self.univariate_categorical_report.bivariate_summaries is None

        assert self.univariate_numeric_report.bivariate_graphs is None
        assert self.univariate_categorical_report.bivariate_graphs is None


def test_output_file(temp_data_dir):
    get_word_report(range(50), output_filename=temp_data_dir / "eda.docx")
    assert (temp_data_dir / "eda.docx").is_file()
