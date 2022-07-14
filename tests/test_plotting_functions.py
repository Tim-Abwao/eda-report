from io import BytesIO

from eda_report.multivariate import MultiVariable
from eda_report.plotting import BasePlot, BivariatePlots, UnivariatePlots
from eda_report.univariate import Variable
from pandas import Series


class TestBasePlot:

    base_plot = BasePlot(graph_color="purple", hue=range(8))

    def test_color(self):
        assert self.base_plot.GRAPH_COLOR == "purple"

    def test_hue(self):
        assert self.base_plot.HUE.equals(Series(range(8)))


class TestBivariatePlots:

    data = MultiVariable([["a", 1, 2], ["b", 2, 3]])
    plots = BivariatePlots(data, graph_color="blue", hue=data.data["var_1"])

    def test_graph_color(self):
        assert self.plots.GRAPH_COLOR == "blue"

    def test_graphs(self):
        assert "correlation_heatmap" in self.plots.graphs
        assert "regression_plots" in self.plots.graphs

    def test_graph_types(self):
        # Graphs are stored as file-like objects
        assert isinstance(self.plots.graphs["correlation_heatmap"], BytesIO)

        for scatter_plot in self.plots.graphs["regression_plots"].values():
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

    def test_numeric_graphs(self):
        for kind, buffer in self.graphs.graphs["numeric"].items():
            assert kind in {"box_plot", "kde_plot", "prob_plot"}
            assert isinstance(buffer, BytesIO)

    def test_categorical_graphs(self):
        for kind, buffer in self.graphs.graphs["categorical"].items():
            assert kind in {"bar_plot"}
            assert isinstance(buffer, BytesIO)
