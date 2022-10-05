from io import BytesIO

import matplotlib as mpl
import pytest
from eda_report.multivariate import MultiVariable
from eda_report.plotting import (
    _plot_multivariable,
    _plot_regression,
    _plot_variable,
    bar_plot,
    box_plot,
    kde_plot,
    plot_correlation,
    prob_plot,
    savefig,
    set_custom_palette,
)
from eda_report.univariate import Variable
from matplotlib.colors import to_rgb
from matplotlib.figure import Figure
from pandas import DataFrame, Series


def test_savefig_function():
    saved = savefig(figure=Figure())
    assert isinstance(saved, BytesIO)


class TestSetCustomPalette:
    # Desired_color will be first, (0.25, 0.25, 0.25) last.

    def test_int_hue(self):
        desired_color = "red"
        hue = 5
        set_custom_palette(color=desired_color, hue=hue)

        colors = mpl.rcParams["axes.prop_cycle"].by_key().get("color")
        assert to_rgb(desired_color) == pytest.approx(colors[0])
        assert (0.25, 0.25, 0.25) == pytest.approx(colors[-1])
        assert len(colors) == hue

    def test_iterable_hue(self):
        desired_color = "green"
        hue = list("abcdeabcdabcaba")
        set_custom_palette(color=desired_color, hue=hue)

        colors = mpl.rcParams["axes.prop_cycle"].by_key().get("color")
        assert to_rgb(desired_color) == pytest.approx(colors[0])
        assert (0.25, 0.25, 0.25) == pytest.approx(colors[-1])
        assert len(colors) == 5  # cardinality of hue

    def test_null_hue(self):
        desired_color = "blue"
        set_custom_palette(color=desired_color)

        colors = mpl.rcParams["axes.prop_cycle"].by_key().get("color")
        assert to_rgb(desired_color) == pytest.approx(colors[0])
        assert (0.25, 0.25, 0.25) == pytest.approx(colors[-1])
        assert len(colors) == 2

    def test_invalid_hue(self):
        with pytest.raises(TypeError) as error:
            set_custom_palette("#eee", 1.25)

        assert (
            "Invalid hue input. Expected an int or an iterable, but got 1.25"
        ) in str(error.value)


class TestBoxplot:
    data = Series(list(range(25)) + [None, None])
    hue = Series([1, 2, 3] * 9)
    simple_box = box_plot(data, label="simple")
    grouped_box = box_plot(data, label="grouped", hue=hue)

    def test_return_type(self):
        assert isinstance(self.simple_box, Figure)
        assert isinstance(self.grouped_box, Figure)

    def test_plot_title(self):
        assert self.simple_box.axes[0].get_title() == "Box-plot of simple"
        assert self.grouped_box.axes[0].get_title() == "Box-plot of grouped"

    def test_grouping(self):
        # Simple bar has one patch
        assert len(self.simple_box.axes[0].patches) == 1
        # Grouped bar has hue.nunique() patches
        assert len(self.grouped_box.axes[0].patches) == self.hue.nunique()


class TestKdeplot:
    data = Series(list(range(25)) + [None, None])
    hue = Series([1, 2, 3] * 9)
    simple_kde = kde_plot(data, label="simple")
    grouped_kde = kde_plot(data, label="grouped", hue=hue)

    def test_return_type(self):
        assert isinstance(self.simple_kde, Figure)
        assert isinstance(self.grouped_kde, Figure)

    def test_plot_title(self):
        assert self.simple_kde.axes[0].get_title() == "Density plot of simple"
        assert (
            self.grouped_kde.axes[0].get_title() == "Density plot of grouped"
        )

    def test_grouping(self):
        # simple_kde has one line
        assert len(self.simple_kde.axes[0].lines) == 1
        # grouped_kde has hue.nunique() lines
        assert len(self.grouped_kde.axes[0].lines) == self.hue.nunique()

    def test_kde_small_sample(self):
        # Should plot text explaining that the input data is singular
        plot = kde_plot(self.data[:1], label="small-sample")
        assert (
            plot.axes[0].texts[0].get_text()
            == "[Could not plot kernel density estimate.\n Data is singular.]"
        )

    def test_kde_zero_variance(self):
        # Should plot text explaining that the input data is singular
        plot = kde_plot(Series([1] * 25), label="constant-sample")
        assert (
            plot.axes[0].texts[0].get_text()
            == "[Could not plot kernel density estimate.\n Data is singular.]"
        )


class TestProbplot:
    data = Series(list(range(25)) + [None, None])
    plot = prob_plot(data, label="some-data")

    def test_return_type(self):
        assert isinstance(self.plot, Figure)

    def test_plot_title(self):
        assert self.plot.axes[0].get_title() == "Probability plot of some-data"

    def test_plot_components(self):
        # Plot should have 2 lines (input data & normal diagonal)
        assert len(self.plot.axes[0].lines) == 2


class TestBarplot:

    low_cardinality_data = Series(list("abcdeabcdabcaba"))
    high_cardinality_data = Series(list("aabbccddeeffgghhiijjkkllmmnn"))
    simple_bar = bar_plot(low_cardinality_data, label="abcde")
    truncated_bar = bar_plot(high_cardinality_data, label="a_to_n")

    def test_return_type(self):
        assert isinstance(self.simple_bar, Figure)
        assert isinstance(self.truncated_bar, Figure)

    def test_plot_title(self):
        assert self.simple_bar.axes[0].get_title() == "Bar-plot of abcde"
        assert (
            self.truncated_bar.axes[0].get_title()
            == "Bar-plot of a_to_n (Top 10 of 14)"
        )

    def test_bar_truncation(self):
        # Check that only the top 10 categories are plotted
        assert len(self.truncated_bar.axes[0].patches) == 10  # only 10 of 14


class TestPlotvariable:
    def test_numeric_plots(self):
        numeric_var = Variable(range(25), name="numbers")
        name, graphs = _plot_variable(
            variables_hue_and_color=(numeric_var, None, "teal")
        )

        assert name == numeric_var.name
        assert set(graphs.keys()) == {"box_plot", "kde_plot", "prob_plot"}
        for graph in graphs.values():
            assert isinstance(graph, BytesIO)

    def test_categorical_plots(self):
        categorical_var = Variable(list("abcdeabcdabcaba"), name="letters")
        name, graphs = _plot_variable(
            variables_hue_and_color=(categorical_var, None, "navy")
        )

        assert name == categorical_var.name
        assert set(graphs.keys()) == {"bar_plot"}
        for graph in graphs.values():
            assert isinstance(graph, BytesIO)


class TestPlotCorrelation:
    def test_with_few_numeric_pairs(self):
        corr_plot = plot_correlation([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        assert isinstance(corr_plot, Figure)
        assert corr_plot.axes[0].get_title() == "Pearson Correlation (Top 3)"
        assert len(corr_plot.axes[0].patches) == 3  # 3 unique pairs

    def test_with_excess_numeric_pairs(self):
        # Should only plot the top 20 by magnitude
        corr_plot = plot_correlation([range(10), [4, 5, 6, 7, 8] * 2])

        assert isinstance(corr_plot, Figure)
        assert corr_plot.axes[0].get_title() == "Pearson Correlation (Top 20)"
        assert len(corr_plot.axes[0].patches) == 20  # Top 20 of 45 pairs


def testplot_regression_function():
    data = DataFrame({"A": range(60000), "B": [1, 2, 3] * 20000})
    var_pair, reg_plot = _plot_regression(data_and_color=(data, "lime"))

    assert var_pair == ("A", "B")
    assert isinstance(reg_plot, Figure)
    assert "Slope" in reg_plot.axes[0].get_title()

    # Check that a sample of size 50000 is taken for large datasets
    points = reg_plot.axes[0].collections[0].get_offsets().data
    assert len(points) == 50000


class TestPlotMultivariable:
    def test_without_numeric_pairs(self):
        data = MultiVariable(range(50))
        assert _plot_multivariable(data, color="red") is None

    def test_with_numeric_pairs(self):
        data = MultiVariable([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        graphs = _plot_multivariable(data, color="green")

        assert set(graphs.keys()) == {
            "correlation_plot",
            "regression_plots",
        }
        corr_plot = graphs["correlation_plot"]
        reg_plots = list(graphs["regression_plots"].values())

        for graph in reg_plots + [corr_plot]:
            assert isinstance(graph, BytesIO)
