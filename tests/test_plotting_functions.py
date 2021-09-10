from eda_report.plotting import PlotMultiVariate, PlotUnivariate, BasePlot
from eda_report.univariate import Variable
from eda_report.multivariate import MultiVariable
from io import BytesIO


class TestBasePlot:

    with_constant_hue = BasePlot(graph_color="navy", hue=[1] * 7)
    with_valid_hue = BasePlot(graph_color="purple", hue=range(8))
    with_high_cardinality = BasePlot(graph_color="yellow", hue=range(15))

    def test_color(self):
        assert self.with_constant_hue.GRAPH_COLOR == "navy"
        assert self.with_valid_hue.GRAPH_COLOR == "purple"
        assert self.with_high_cardinality.GRAPH_COLOR == "yellow"

    def test_color_coding(self):
        # Should be False with constant and high cardinality hues
        assert self.with_constant_hue.COLOR_CODE_GRAPHS is False
        assert self.with_valid_hue.COLOR_CODE_GRAPHS
        assert self.with_high_cardinality.COLOR_CODE_GRAPHS is False


class TestPlotMultiVariate:

    data = MultiVariable([["a", 1, 2], ["b", 2, 3]])
    plots = PlotMultiVariate(data, graph_color="blue", hue=data.data["var_1"])

    def test_graph_color(self):
        assert self.plots.GRAPH_COLOR == "blue"

    def test_color_coding(self):
        assert self.plots.COLOR_CODE_GRAPHS
        # The heatmap and pairwise scatterplots need no color coding
        assert self.plots._COLOR_CODED_GRAPHS == set()

    def test_graphs(self):
        assert "correlation_heatmap" in self.plots.graphs
        assert "scatterplots" in self.plots.graphs

    def test_graph_types(self):
        assert isinstance(self.plots.graphs["correlation_heatmap"], BytesIO)

        for scatter_plot in self.plots.graphs["scatterplots"].values():
            assert isinstance(scatter_plot, BytesIO)


class TestPlotUnivariate:

    numeric_variable = Variable(range(7))
    categorical_variable = Variable(list("abcde"))

    plots_numeric = PlotUnivariate(numeric_variable, hue=list("abcacba"))
    plots_categorical = PlotUnivariate(
        categorical_variable, graph_color="olive", hue=range(5)
    )

    def test_graph_color(self):
        assert self.plots_numeric.GRAPH_COLOR == "cyan"
        assert self.plots_categorical.GRAPH_COLOR == "olive"

    def test_color_coding(self):
        assert self.plots_numeric._COLOR_CODED_GRAPHS == {
            "boxplot",
            "histogram",
            "run-plot",
        }
        assert self.plots_categorical._COLOR_CODED_GRAPHS == {"bar_plot"}

    def test_graphs(self):
        assert list(self.plots_numeric.graphs.keys()) == [
            "boxplot",
            "histogram",
            "prob_plot",
            "run_plot",
        ]
        assert "bar_plot" in self.plots_categorical.graphs

    def test_graph_types(self):
        for plot in self.plots_numeric.graphs.values():
            assert isinstance(plot, BytesIO)

        for plot in self.plots_categorical.graphs.values():
            assert isinstance(plot, BytesIO)
