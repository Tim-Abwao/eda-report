from io import BytesIO

from eda_report.multivariate import MultiVariable
from eda_report.plotting import BasePlot, BivariatePlots, UnivariatePlots
from eda_report.univariate import Variable


class TestBasePlot:

    with_constant_hue = BasePlot(graph_color="navy", hue=[1] * 7)
    with_valid_hue = BasePlot(graph_color="purple", hue=range(8))
    with_high_cardinality = BasePlot(graph_color="yellow", hue=range(15))

    def test_color(self):
        assert self.with_constant_hue.GRAPH_COLOR == "navy"
        assert self.with_valid_hue.GRAPH_COLOR == "purple"
        assert self.with_high_cardinality.GRAPH_COLOR == "yellow"


class TestBivariatePlots:

    data = MultiVariable([["a", 1, 2], ["b", 2, 3]])
    plots = BivariatePlots(data, graph_color="blue", hue=data.data["var_1"])

    def test_graph_color(self):
        assert self.plots.GRAPH_COLOR == "blue"

    def test_graphs(self):
        assert "correlation_heatmap" in self.plots.graphs
        assert "scatterplots" in self.plots.graphs

    def test_graph_types(self):
        assert isinstance(self.plots.graphs["correlation_heatmap"], BytesIO)

        for scatter_plot in self.plots.graphs["scatterplots"].values():
            assert isinstance(scatter_plot, BytesIO)


class TestUnivariatePlots:

    numeric_variable = Variable(range(15), name="numeric")
    categorical_variable = Variable(
        list("abcdefghijklmno"), name="categorical"
    )

    graphs = UnivariatePlots(
        [categorical_variable, numeric_variable],
        graph_color="olive",
        hue=[1, 2, 3] * 5,
    )

    def test_graph_color(self):
        assert self.graphs.GRAPH_COLOR == "olive"

    def test_graphs(self):
        assert set(self.graphs.graphs["numeric"].keys()) == {
            "box_plot",
            "kde_plot",
            "prob_plot",
        }
        assert "bar_plot" in self.graphs.graphs["categorical"]

    def test_graph_types(self):
        for plot in self.graphs.graphs["numeric"].values():
            assert isinstance(plot, BytesIO)

        for plot in self.graphs.graphs["categorical"].values():
            assert isinstance(plot, BytesIO)
