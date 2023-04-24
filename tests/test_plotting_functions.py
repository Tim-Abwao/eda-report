from io import BytesIO

import pytest
from matplotlib.colors import to_rgb
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from pandas import DataFrame, Series

from eda_report.bivariate import Dataset
from eda_report.plotting import (
    _get_color_shades_of,
    _plot_dataset,
    _plot_regression,
    _plot_variable,
    _savefig,
    _get_axes,
    bar_plot,
    box_plot,
    kde_plot,
    plot_correlation,
    prob_plot,
)
from eda_report.univariate import Variable


def test_savefig_function():
    saved = _savefig(figure=Figure())
    assert isinstance(saved, BytesIO)


def test_get_color_shades_of():
    color, num_shades = "green", 5
    green_shades = _get_color_shades_of(color, num_shades)
    assert green_shades.shape == (num_shades, 3)  # each color is an rgb tuple
    assert green_shades[0] == pytest.approx(to_rgb(color))


class TestGetAxesFunction:
    def test_without_input(self):
        ax = _get_axes()
        assert isinstance(ax, Axes)

    def test_with_axes_input(self):
        ax1 = Figure().subplots()
        ax2 = _get_axes(ax1)
        assert ax1 is ax2

    def test_with_invalid_input(self):
        with pytest.raises(TypeError) as error:
            _get_axes(123)
        # Check that the error message is as expected
        assert "Invalid input for 'ax': <class 'int'>" in str(error.value)


class TestBoxplot:
    data = Series(list(range(25)) + [None, None])
    hue = Series([1, 2, 3] * 9, name="hue-name")
    simple_box = box_plot(data, label="simple")
    grouped_box = box_plot(data, label="grouped", hue=hue)

    def test_return_type(self):
        assert isinstance(self.simple_box, Axes)
        assert isinstance(self.grouped_box, Axes)

    def test_plot_title(self):
        assert self.simple_box.get_title() == "Box-plot of simple"
        assert self.grouped_box.get_title() == "Box-plot of grouped"

    def test_axis_labels(self):
        assert self.simple_box.get_xlabel() == ""
        assert self.simple_box.get_ylabel() == ""
        assert self.grouped_box.get_xlabel() == ""
        assert self.grouped_box.get_ylabel() == "Hue-Name"

        boxplot_with_nameless_hue = box_plot(
            self.data, label="grouped", hue=self.hue.to_numpy()
        )
        assert boxplot_with_nameless_hue.get_xlabel() == ""
        assert boxplot_with_nameless_hue.get_ylabel() == ""

    def test_grouping(self):
        # Simple box-plot has one patch
        assert len(self.simple_box.patches) == 1
        # Grouped box-plot has hue.nunique() patches
        assert len(self.grouped_box.patches) == self.hue.nunique()

    def test_simple_set_color(self):
        box1_color = self.simple_box.patches[0].get_facecolor()

        _color = "blue"
        simple_box_2 = box_plot(self.data, label="simple", color=_color)
        box2_color = simple_box_2.patches[0].get_facecolor()

        assert box1_color == pytest.approx(
            (*to_rgb("C0"), 0.75)  # default color 1 and alpha value
        )
        assert box2_color == pytest.approx(
            (*to_rgb(_color), 0.75)  # _color and alpha value
        )

    def test_grouped_set_color(self):
        _color = "lime"
        # Take last patch since colors are reversed (["CN", .. , "C0"])
        last_box_color = self.grouped_box.patches[-1].get_facecolor()

        grouped_box_2 = box_plot(
            self.data, hue=self.hue, label="simple", color=_color
        )
        last_box2_color = grouped_box_2.patches[-1].get_facecolor()

        assert last_box_color == pytest.approx(
            (*to_rgb("C0"), 0.75)  # default color |hue| and alpha value
        )
        assert last_box2_color == pytest.approx(
            (*to_rgb(_color), 0.75)  # _color and alpha value
        )


class TestKdeplot:
    data = Series(list(range(25)) + [None, None])
    hue = Series([1, 2, 3] * 9, name="hue-name")
    simple_kde = kde_plot(data, label="simple")
    grouped_kde = kde_plot(data, label="grouped", hue=hue)

    def test_return_type(self):
        assert isinstance(self.simple_kde, Axes)
        assert isinstance(self.grouped_kde, Axes)

    def test_plot_title(self):
        assert self.simple_kde.get_title() == "Density plot of simple"
        assert self.grouped_kde.get_title() == "Density plot of grouped"

    def test_axis_labels(self):
        assert self.simple_kde.get_xlabel() == "simple"
        assert self.simple_kde.get_ylabel() == ""
        assert self.grouped_kde.get_xlabel() == "grouped"
        assert self.grouped_kde.get_ylabel() == ""

    def test_legend(self):
        assert self.simple_kde.get_legend() is None
        assert (
            self.grouped_kde.get_legend().get_title().get_text() == "Hue-Name"
        )
        grouped_with_nameless_hue = kde_plot(
            self.data, label="grouped", hue=self.hue.to_numpy()
        )
        assert grouped_with_nameless_hue.get_legend() is None

    def test_grouping(self):
        # simple_kde has one line
        assert len(self.simple_kde.lines) == 1
        # grouped_kde has hue.nunique() lines
        assert len(self.grouped_kde.lines) == self.hue.nunique()

    def test_kde_small_sample(self):
        # Should plot text explaining that the input data is singular
        plot = kde_plot(self.data[:1], label="small-sample")
        assert (
            plot.texts[0].get_text()
            == "[Could not plot kernel density estimate.\n Data is singular.]"
        )

    def test_kde_zero_variance(self):
        # Should plot text explaining that the input data is singular
        plot = kde_plot(Series([1] * 25), label="constant-sample")
        assert (
            plot.texts[0].get_text()
            == "[Could not plot kernel density estimate.\n Data is singular.]"
        )

    def test_simple_set_color(self):
        kde1_color = self.simple_kde.lines[0].get_color()

        _color = "violet"
        simple_kde_2 = kde_plot(self.data, label="simple", color=_color)
        kde2_color = simple_kde_2.lines[0].get_color()

        assert to_rgb(kde1_color) == pytest.approx(to_rgb("C0"))
        assert to_rgb(kde2_color) == pytest.approx(to_rgb(_color))

    def test_grouped_set_color(self):
        first_kde_color = self.grouped_kde.lines[0].get_color()

        _color = "aqua"
        grouped_kde_2 = kde_plot(
            self.data, hue=self.hue, label="simple", color=_color
        )
        first_kde2_color = grouped_kde_2.lines[0].get_color()

        assert to_rgb(first_kde_color) == pytest.approx(to_rgb("C0"))
        assert to_rgb(first_kde2_color) == pytest.approx(to_rgb(_color))


class TestProbplot:
    data = Series(list(range(25)) + [None, None])
    plot = prob_plot(data, label="some-data")

    def test_return_type(self):
        assert isinstance(self.plot, Axes)

    def test_plot_title(self):
        assert self.plot.get_title() == "Probability plot of some-data"

    def test_axis_labels(self):
        assert self.plot.get_xlabel() == "Theoretical Quantiles (Normal)"
        assert self.plot.get_ylabel() == "Ordered Values"

    def test_plot_components(self):
        # Plot should have 2 lines (input data & normal diagonal)
        assert len(self.plot.lines) == 2

    def test_default_colors(self):
        markers, reg_line = self.plot.lines

        assert markers.get_color() == "C0"
        assert reg_line.get_color() == "#222"

    def test_set_colors(self):
        fig = prob_plot(
            self.data,
            label="some-more-data",
            marker_color="yellow",
            line_color="salmon",
        )
        markers, reg_line = fig.lines

        assert markers.get_color() == "yellow"
        assert reg_line.get_color() == "salmon"


class TestBarplot:
    low_cardinality_data = Series(list("abcdeabcdabcaba"))
    high_cardinality_data = Series(list("aabbccddeeffgghhiijjkkllmmnn"))
    simple_bar = bar_plot(low_cardinality_data, label="abcde")
    truncated_bar = bar_plot(high_cardinality_data, label="a_to_n")

    def test_return_type(self):
        assert isinstance(self.simple_bar, Axes)
        assert isinstance(self.truncated_bar, Axes)

    def test_plot_title(self):
        assert self.simple_bar.get_title() == "Bar-plot of abcde"
        assert (
            self.truncated_bar.get_title()
            == "Bar-plot of a_to_n (Top 10 of 14)"
        )

    def test_axis_labels(self):
        assert self.simple_bar.get_xlabel() == ""
        assert self.simple_bar.get_ylabel() == "Count"

    def test_bar_truncation(self):
        # Check that only the top 10 categories are plotted
        assert len(self.truncated_bar.patches) == 10  # only 10 of 14

    def test_default_color(self):
        bar_color = self.simple_bar.patches[0].get_facecolor()
        assert to_rgb(bar_color) == pytest.approx(to_rgb("C0"))

    def test_set_color(self):
        fig = bar_plot(self.low_cardinality_data, label="test", color="pink")
        bar_color = fig.patches[0].get_facecolor()
        assert to_rgb(bar_color) == pytest.approx(to_rgb("pink"))


class TestPlotvariable:
    def test_numeric_plots(self):
        data = range(25)
        numeric_var = Variable(data, name="numbers")
        name, graphs = _plot_variable(
            variable_data_hue_and_color=(numeric_var, data, None, "teal")
        )

        assert name == numeric_var.name
        assert set(graphs.keys()) == {"box_plot", "kde_plot", "prob_plot"}
        for graph in graphs.values():
            assert isinstance(graph, BytesIO)

    def test_categorical_plots(self):
        data = list("abcdeabcdabcaba")
        categorical_var = Variable(list("abcdeabcdabcaba"), name="letters")
        name, graphs = _plot_variable(
            variable_data_hue_and_color=(categorical_var, data, None, "navy")
        )

        assert name == categorical_var.name
        assert set(graphs.keys()) == {"bar_plot"}
        for graph in graphs.values():
            assert isinstance(graph, BytesIO)


class TestPlotCorrelation:
    def test_with_insufficient_numeric_pairs(self):
        # Check None is returned if there are < 2 numeric pairs
        single_numeric = plot_correlation(zip(range(5), list("abcde")))
        no_numeric = plot_correlation(list("abcde"))
        assert single_numeric is None
        assert no_numeric is None

    def test_with_few_numeric_pairs(self):
        corr_plot = plot_correlation([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        assert isinstance(corr_plot, Axes)
        assert corr_plot.get_title() == "Pearson Correlation (Top 3)"
        assert len(corr_plot.patches) == 3  # 3 unique pairs

    def test_with_excess_numeric_pairs(self):
        # Should only plot the top 20 by magnitude
        corr_plot = plot_correlation([range(10), [4, 5, 6, 7, 8] * 2])

        assert isinstance(corr_plot, Axes)
        assert corr_plot.get_title() == "Pearson Correlation (Top 20)"
        assert len(corr_plot.patches) == 20  # Top 20 of 45 pairs

    def test_default_colors(self):
        corr_plot = plot_correlation([[1, 2, 8], [3, 5, 5], [9, 8, 1]])
        bars = corr_plot.patches
        # bars = (0.96, -0.98, -1), from origin
        pos_bar_color = bars[0].get_facecolor()
        neg_bar_color = bars[-1].get_facecolor()

        assert to_rgb(pos_bar_color) == pytest.approx(to_rgb("orangered"))
        assert to_rgb(neg_bar_color) == pytest.approx(to_rgb("steelblue"))

    def test_set_colors(self):
        corr_plot2 = plot_correlation(
            [[10, 20, 80], [30, 50, 50], [90, 80, 10]],
            color_neg="skyblue",
            color_pos="maroon",
        )
        bars2 = corr_plot2.patches
        # bars = (0.96, -0.98, -1), from origin
        pos_bar_color2 = bars2[0].get_facecolor()
        neg_bar_color2 = bars2[-1].get_facecolor()

        assert to_rgb(pos_bar_color2) == pytest.approx(to_rgb("maroon"))
        assert to_rgb(neg_bar_color2) == pytest.approx(to_rgb("skyblue"))


class TestRegressionPlot:
    data = DataFrame({"A": range(60000), "B": [1, 2, 3] * 20000})
    var_pair, reg_plot = _plot_regression(data_and_color=(data, "lime"))

    def test_return_type(self):
        assert self.var_pair == ("A", "B")
        assert isinstance(self.reg_plot, Axes)

    def test_plot_title(self):
        title = self.reg_plot.get_title()
        assert "Slope" in title
        assert "Intercept" in title
        assert "Correlation" in title

    def test_axis_labels(self):
        var1, var2 = self.var_pair
        assert self.reg_plot.get_xlabel() == var1
        assert self.reg_plot.get_ylabel() == var2

    def test_max_sample_size(self):
        # Check that a sample of size 50000 is taken for large datasets
        points = self.reg_plot.collections[0].get_offsets().data
        assert len(points) == 50000

    def test_plot_color(self):
        assert self.reg_plot.lines[0].get_color() == "#444"  # reg line
        assert to_rgb(  # markers
            self.reg_plot.collections[0].get_facecolor()
        ) == pytest.approx(to_rgb("lime"))


class TestPlotDataset:
    def test_without_numeric_pairs(self):
        data = Dataset(range(50))
        assert _plot_dataset(data, color="red") is None

    def test_with_numeric_pairs(self):
        data = Dataset([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        graphs = _plot_dataset(data, color="green")

        assert set(graphs.keys()) == {
            "correlation_plot",
            "regression_plots",
        }
        corr_plot = graphs["correlation_plot"]
        reg_plots = list(graphs["regression_plots"].values())

        for graph in reg_plots + [corr_plot]:
            assert isinstance(graph, BytesIO)

    def test_limiting_numeric_pairs(self):
        data = Dataset([range(12), [1, 2, 3, 4] * 3])
        # `data`` has 12 numeric columns, resulting in up to 66 var_pairs.
        # Check if only limit = 20 are plotted.
        graphs = _plot_dataset(data, color="green")
        assert len(graphs["regression_plots"]) == 20
