from io import BytesIO

from eda_report.content import (
    _AnalysisResult,
    _ReportContent,
    _get_contingency_tables,
)
from eda_report.multivariate import MultiVariable
from eda_report.univariate import _CategoricalStats, _NumericStats
from pandas import DataFrame, Series

data = DataFrame(
    {"A": range(50), "B": [1, 2, 3, 4, 5] * 10, "C": list("ab") * 25}
)


class TestGetContingencyTables:
    data = DataFrame(
        [list("abc"), list("abd"), list("bcd")] * 4, columns=list("ABC")
    )

    def test_with_empty_data(self):
        empty_df = self.data[[]]
        tables = _get_contingency_tables(
            categorical_df=empty_df, groupby_data=self.data["C"]
        )
        assert tables == {}

    def test_with_null_groupby_data(self):
        tables = _get_contingency_tables(
            categorical_df=self.data, groupby_data=None
        )
        assert tables == {}

    def test_with_valid_args(self):
        tables = _get_contingency_tables(
            categorical_df=self.data, groupby_data=self.data["C"]
        )
        # Check that groupby_data "C" is not included
        assert set(tables.keys()) == {"A", "B"}
        assert tables["A"].to_dict() == {
            "c": {"a": 4, "b": 0, "Total": 4},
            "d": {"a": 4, "b": 4, "Total": 8},
            "Total": {"a": 8, "b": 4, "Total": 12},
        }
        assert tables["B"].to_dict() == {
            "c": {"b": 4, "c": 0, "Total": 4},
            "d": {"b": 4, "c": 4, "Total": 8},
            "Total": {"b": 8, "c": 4, "Total": 12},
        }

    def test_cardinality_limit(self):
        high_cardinality_data = DataFrame(
            {
                "A": range(50),
                "B": list("abcdefghijklmnopqrstuvwxy") * 2,
                "C": list(range(10)) * 5,
            }
        )
        tables = _get_contingency_tables(
            categorical_df=high_cardinality_data,
            groupby_data=Series([1, 2] * 25),
        )
        # "A" and "B" have > 20 unique values, and so are omitted
        assert set(tables.keys()) == {"C"}


class TestAnalysisResult:
    results = _AnalysisResult(data, graph_color="green", groupby_data="C")

    def test_general_properties(self):
        assert isinstance(self.results.multivariable, MultiVariable)
        assert self.results.GRAPH_COLOR == "green"
        assert self.results.GROUPBY_DATA.equals(data["C"])
        assert self.results.bivariate_summaries == {
            ("A", "B"): "A and B have very weak positive correlation (0.10)."
        }

    def test_analyzed_variables(self):
        assert isinstance(
            self.results.analyzed_variables["A"].summary_statistics,
            _NumericStats,
        )
        assert isinstance(
            self.results.analyzed_variables["B"].summary_statistics,
            _CategoricalStats,
        )
        assert isinstance(
            self.results.analyzed_variables["C"].summary_statistics,
            _CategoricalStats,
        )

    def test_univariate_graphs(self):
        for key, graphs in self.results.univariate_graphs.items():
            assert key in set("ABC")
            for graph in graphs.values():
                assert isinstance(graph, BytesIO)

    def test_univariate_statistics(self):
        assert set(self.results.univariate_stats) == {"A", "B", "C"}
        for stats in self.results.univariate_stats.values():
            assert isinstance(stats, DataFrame)

    def test_normality_tests(self):
        assert set(self.results.normality_tests) == {"A"}

        for df in self.results.normality_tests.values():
            assert set(df.index) == {
                "D'Agostino's K-squared test",
                "Shapiro-Wilk test",
                "Kolmogorov-Smirnov test",
            }

    def test_contingency_tables(self):
        assert set(self.results.contingency_tables) == {"B"}
        assert self.results.contingency_tables["B"].to_dict() == {
            "a": {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, "Total": 25},
            "b": {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, "Total": 25},
            "Total": {1: 10, 2: 10, 3: 10, 4: 10, 5: 10, "Total": 50},
        }

    def test_bivariate_graphs(self):
        assert set(self.results.bivariate_graphs.keys()) == {
            "correlation_plot",
            "regression_plots",
        }
        assert isinstance(
            self.results.bivariate_graphs["correlation_plot"], BytesIO
        )
        for graph in self.results.bivariate_graphs[
            "regression_plots"
        ].values():
            assert isinstance(graph, BytesIO)


class TestReportContent:
    content = _ReportContent(data, title="Some Title")

    def test_general_attributes(self):
        assert isinstance(self.content, _AnalysisResult)
        assert self.content.GRAPH_COLOR == "cyan"
        assert self.content.TITLE == "Some Title"
        assert self.content.GROUPBY_DATA is None

    def test_intro(self):
        assert self.content.intro_text == (
            "The dataset consists of 50 rows (observations) and 3 columns "
            "(features), 2 of which are numeric."
        )

    def test_variable_descriptions(self):
        desc_A = self.content.variable_descriptions["A"]

        assert desc_A == (
            "A is a numeric variable with 50 unique values. None of its values"
            " are missing."
        )

    def test_bivariate_summaries(self):
        assert self.content.bivariate_summaries == {
            ("A", "B"): "A and B have very weak positive correlation (0.10)."
        }


def test_limiting_bivariate_summaries():
    content = _ReportContent([range(12), [1, 2, 3, 4] * 3])
    # content has 66 var_pairs, but the limit for summaries is 20
    assert len(content.bivariate_summaries) == 20
