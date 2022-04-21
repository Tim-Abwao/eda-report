from io import BytesIO

from eda_report.content import AnalysisResult, ReportContent
from eda_report.multivariate import MultiVariable
from eda_report.univariate import CategoricalStats, NumericStats
from seaborn import load_dataset

data = load_dataset("iris")


class TestAnalysisResult:
    results = AnalysisResult(data)

    def test_overall_statistics(self):
        assert isinstance(self.results.multivariable, MultiVariable)
        assert self.results.multivariable.categorical_stats.to_dict() == {
            "count": {"species": 150},
            "unique": {"species": 3},
            "top": {"species": "setosa"},
            "freq": {"species": 50},
            "relative freq": {"species": "33.33%"},
        }

    def test_univariate_stats(self):
        assert set(self.results.univariate_stats.keys()) == {
            "petal_length",
            "sepal_width",
            "species",
            "petal_width",
            "sepal_length",
        }
        assert isinstance(
            self.results.univariate_stats["species"], CategoricalStats
        )
        assert isinstance(
            self.results.univariate_stats["sepal_width"], NumericStats
        )

    def test_univariate_graphs(self):
        assert set(self.results.univariate_graphs.keys()) == {
            "petal_length",
            "sepal_width",
            "species",
            "petal_width",
            "sepal_length",
        }
        for graph in self.results.univariate_graphs["petal_length"].values():
            assert isinstance(graph, BytesIO)

    def test_bivariate_graphs(self):
        assert set(self.results.bivariate_graphs.keys()) == {
            "correlation_heatmap",
            "scatterplots",
        }
        assert isinstance(
            self.results.bivariate_graphs["correlation_heatmap"], BytesIO
        )


class TestReportContent:
    content = ReportContent(
        data,
        title="Some Title",
        graph_color="magenta",
        target_variable="species",
    )

    def test_general_attributes(self):
        assert isinstance(self.content, AnalysisResult)
        assert self.content.GRAPH_COLOR == "magenta"
        assert self.content.TITLE == "Some Title"
        assert self.content.TARGET_VARIABLE.equals(data["species"])

    def test_intro(self):
        assert self.content.intro_text == (
            "The dataset consists of 150 rows (observations) and 5 columns "
            "(features), 4 of which are numeric."
        )

    def test_variable_info(self):
        species_info = self.content.variable_info["species"]
        assert set(species_info.keys()) == {
            "description",
            "graphs",
            "statistics",
            "normality_tests",
        }
        assert species_info["description"] == (
            "Species is a categorical variable with 3 unique values. "
            "None of its values are missing."
        )

    def test_bivariate_summaries(self):
        assert self.content.bivariate_summaries == {
            ("sepal_width", "petal_length"): (
                "Sepal_Width and Petal_Length have weak negative correlation"
                " (-0.43)."
            ),
            ("sepal_length", "sepal_width"): (
                "Sepal_Length and Sepal_Width have very weak negative "
                "correlation (-0.12)."
            ),
            ("sepal_width", "petal_width"): (
                "Sepal_Width and Petal_Width have weak negative correlation"
                " (-0.37)."
            ),
            ("petal_length", "petal_width"): (
                "Petal_Length and Petal_Width have very strong positive "
                "correlation (0.96)."
            ),
            ("sepal_length", "petal_length"): (
                "Sepal_Length and Petal_Length have strong positive "
                "correlation (0.87)."
            ),
            ("sepal_length", "petal_width"): (
                "Sepal_Length and Petal_Width have strong positive "
                "correlation (0.82)."
            ),
        }
