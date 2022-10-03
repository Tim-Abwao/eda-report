from io import BytesIO

from eda_report.content import AnalysisResult, ReportContent
from eda_report.multivariate import MultiVariable
from eda_report.univariate import CategoricalStats, NumericStats
from pandas import DataFrame

data = DataFrame(
    {"A": range(50), "B": [1, 2, 3, 4, 5] * 10, "C": list("ab") * 25}
)


class TestAnalysisResult:
    results = AnalysisResult(data, graph_color="green", groupby_data="C")

    def test_general_properties(self):
        assert isinstance(self.results.multivariable, MultiVariable)
        assert self.results.GRAPH_COLOR == "green"
        assert self.results.GROUPBY_DATA.equals(data["C"])

    def test_univariate_stats(self):
        assert isinstance(
            self.results.univariate_stats["A"].summary_statistics, NumericStats
        )
        assert isinstance(
            self.results.univariate_stats["B"].summary_statistics,
            CategoricalStats,
        )
        assert isinstance(
            self.results.univariate_stats["C"].summary_statistics,
            CategoricalStats,
        )

    def test_univariate_graphs(self):
        for key, graphs in self.results.univariate_graphs.items():
            assert key in set("ABC")
            for graph in graphs.values():
                assert isinstance(graph, BytesIO)

    def test_bivariate_graphs(self):
        assert set(self.results.bivariate_graphs.keys()) == {
            "correlation_heatmap",
            "regression_plots",
        }
        assert isinstance(
            self.results.bivariate_graphs["correlation_heatmap"], BytesIO
        )
        for graph in self.results.bivariate_graphs[
            "regression_plots"
        ].values():
            assert isinstance(graph, BytesIO)


class TestReportContent:
    content = ReportContent(data, title="Some Title")

    def test_general_attributes(self):
        assert isinstance(self.content, AnalysisResult)
        assert self.content.GRAPH_COLOR == "cyan"
        assert self.content.TITLE == "Some Title"
        assert self.content.GROUPBY_DATA is None

    def test_intro(self):
        assert self.content.intro_text == (
            "The dataset consists of 50 rows (observations) and 3 columns "
            "(features), 2 of which are numeric."
        )

    def test_variable_info(self):
        A_info = self.content.variable_info["A"]
        assert set(A_info.keys()) == {
            "description",
            "graphs",
            "statistics",
            "normality_tests",
        }
        assert A_info["description"] == (
            "A is a numeric variable with 50 unique values. None of its values"
            " are missing."
        )

    def test_bivariate_summaries(self):
        assert self.content.bivariate_summaries == {
            ("A", "B"): "A and B have very weak positive correlation (0.10)."
        }
