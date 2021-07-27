from eda_report import get_word_report
from pandas.core.frame import DataFrame
from seaborn import load_dataset


class TestReportWithIdealInput:

    data = load_dataset("iris")
    content = get_word_report(
        data,
        title="Test Report",
        graph_color="teal",
        target_variable="species",
    )

    def test_bivariate_analysis(self):
        assert self.content.bivariate_summaries == {
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

    def test_graph_color(self):
        assert self.content.GRAPH_COLOR == "teal"

    def test_intro(self):
        assert self.content.intro_text == (
            "The dataset consists of 150 rows (observations) and 5 columns "
            "(features), 4 of which are numeric."
        )

    def test_bivariate_graphs(self):
        assert "correlation_heatmap" in self.content.multivariate_graphs
        assert "scatterplots" in self.content.multivariate_graphs

    def test_target_data(self):
        assert self.content.TARGET_VARIABLE.equals(self.data["species"])


class TestReportWithLimitedInput:

    data = DataFrame(
        {"categorical": list("ABCDEFGHIJKL"), "numeric": range(12)}
    )
    report = get_word_report(data)

    def test_title(self):
        assert self.report.TITLE == "Exploratory Data Analysis Report"


class TestReportWithUnivariateInput:

    univariate_numeric_report = get_word_report(DataFrame(range(5)))
    univariate_categorical_report = get_word_report(DataFrame(["a"]))

    def test_title(self):
        assert (
            self.univariate_numeric_report.TITLE
            == "Exploratory Data Analysis Report"
        )
        assert (
            self.univariate_categorical_report.TITLE
            == "Exploratory Data Analysis Report"
        )
