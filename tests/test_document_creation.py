from io import BytesIO

from pandas.core.frame import DataFrame

from eda_report.document import ReportDocument


class TestReportWithIdealInput:
    data = DataFrame(
        {"A": range(50), "B": [1, 2, 3, 4, 5] * 10, "C": list("ab") * 25}
    )
    report = ReportDocument(
        data,
        title="Test Report",
        graph_color="teal",
        groupby_data="C",
        output_filename=BytesIO(),
    )

    def test_general_properties(self):
        # Largely covered in _ReportContent tests
        assert self.report.TITLE == "Test Report"
        assert self.report.GRAPH_COLOR == "teal"
        assert "correlation_plot" in self.report.bivariate_graphs
        assert "regression_plots" in self.report.bivariate_graphs
        assert self.report.TABLE_STYLE == "Table Grid"


class TestReportWithLimitedInput:
    data = DataFrame(
        {"categorical": list("ABCDEFGHIJKL" * 2), "numeric": range(24)}
    )
    report = ReportDocument(
        data,
        title="One Numeric One Categorical",
        graph_color="lime",
        output_filename=BytesIO(),
    )

    def test_report_creation(self):
        assert isinstance(self.report, ReportDocument)
        assert self.report.TITLE == "One Numeric One Categorical"
        assert self.report.GRAPH_COLOR == "lime"

    def test_bivariate_analysis(self):
        assert self.report.bivariate_summaries is None
        assert self.report.bivariate_graphs is None


class TestReportWithUnivariateInput:
    univariate_numeric_report = ReportDocument(
        DataFrame(range(5)),
        title="Univariate Numeric Report",
        output_filename=BytesIO(),
    )
    univariate_categorical_report = ReportDocument(
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
    ReportDocument(range(50), output_filename=temp_data_dir / "eda.docx")
    assert (temp_data_dir / "eda.docx").is_file()
