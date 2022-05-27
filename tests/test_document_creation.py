from io import BytesIO

from eda_report import get_word_report
from eda_report.document import ReportDocument
from pandas.core.frame import DataFrame
from seaborn import load_dataset


class TestReportWithIdealInput:

    data = load_dataset("iris")
    report = get_word_report(
        data,
        title="Test Report",
        graph_color="teal",
        target_variable="species",
        output_filename=BytesIO(),
    )

    def test_title(self):
        assert self.report.TITLE == "Test Report"

    def test_graph_color(self):
        assert self.report.GRAPH_COLOR == "teal"

    def test_intro(self):
        assert self.report.intro_text == (
            "The dataset consists of 150 rows (observations) and 5 columns "
            "(features), 4 of which are numeric."
        )

    def test_bivariate_analysis(self):
        assert self.report.bivariate_summaries == {
            ("sepal_length", "petal_length"): (
                "Sepal_Length and Petal_Length have strong positive "
                "correlation (0.87)."
            ),
            ("petal_length", "petal_width"): (
                "Petal_Length and Petal_Width have very strong positive "
                "correlation (0.96)."
            ),
            ("sepal_length", "sepal_width"): (
                "Sepal_Length and Sepal_Width have very weak negative "
                "correlation (-0.12)."
            ),
            ("sepal_length", "petal_width"): (
                "Sepal_Length and Petal_Width have strong positive "
                "correlation (0.82)."
            ),
            ("sepal_width", "petal_length"): (
                "Sepal_Width and Petal_Length have weak negative correlation"
                " (-0.43)."
            ),
            ("sepal_width", "petal_width"): (
                "Sepal_Width and Petal_Width have weak negative correlation "
                "(-0.37)."
            ),
        }

    def test_bivariate_graphs(self):
        assert "correlation_heatmap" in self.report.bivariate_graphs
        assert "regression_plots" in self.report.bivariate_graphs

    def test_table_style(self):
        assert self.report.TABLE_STYLE == "Table Grid"

    def test_target_variable(self):
        assert self.report.TARGET_VARIABLE.equals(self.data["species"])

    def test_variable_info(self):
        assert list(self.report.variable_info.keys()) == [
            "petal_length",
            "petal_width",
            "sepal_length",
            "sepal_width",
            "species",
        ]


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
        assert self.report.TITLE == "One Numeric One Categorical"
        assert isinstance(self.report, ReportDocument)
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


def test_output_file(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    get_word_report(range(50), output_filename=data_dir / "eda.docx")
    assert (tmp_path / "data" / "eda.docx").is_file()
