from io import BytesIO

import pytest
from eda_report.multivariate import MultiVariable
from eda_report.plotting import (
    bar_plot,
    box_plot,
    kde_plot,
    plot_correlation,
    plot_multivariable,
    plot_regression,
    plot_variable,
    prob_plot,
    savefig,
    set_custom_palette,
)
from eda_report.univariate import Variable
from matplotlib.colors import to_rgb
from matplotlib.figure import Figure
from pandas import Series, DataFrame
import matplotlib as mpl


def test_savefig_function():
    saved = savefig(figure=Figure())
    assert isinstance(saved, BytesIO)


def test_set_custom_palette():
    desired_color = "green"
    num_colors = 5
    set_custom_palette(color=desired_color, num=num_colors)

    colors = mpl.rcParams["axes.prop_cycle"].by_key().get("color")
    assert to_rgb(desired_color) == pytest.approx(colors[0])
    assert (0.25, 0.25, 0.25) == pytest.approx(colors[-1])
    assert len(colors) == num_colors


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
        name, graphs = plot_variable(variable_and_hue=(numeric_var, None))

        assert name == numeric_var.name
        assert set(graphs.keys()) == {"box_plot", "kde_plot", "prob_plot"}
        for graph in graphs.values():
            assert isinstance(graph, BytesIO)

    def test_categorical_plots(self):
        categorical_var = Variable(list("abcdeabcdabcaba"), name="letters")
        name, graphs = plot_variable(variable_and_hue=(categorical_var, None))

        assert name == categorical_var.name
        assert set(graphs.keys()) == {"bar_plot"}
        for graph in graphs.values():
            assert isinstance(graph, BytesIO)


class TestPlotCorrelation:
    def test_with_few_numeric_pairs(self):
        variables = MultiVariable([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        corr_plot = plot_correlation(variables)

        assert isinstance(corr_plot, Figure)
        assert corr_plot.axes[0].get_title() == "Pearson Correlation (Top 3)"
        assert len(corr_plot.axes[0].patches) == len(variables.var_pairs)

    def test_with_excess_numeric_pairs(self):
        # Should only plot the top 20 by magnitude
        variables = MultiVariable([range(25), [4, 5, 6, 7, 8] * 5])
        corr_plot = plot_correlation(variables)

        assert isinstance(corr_plot, Figure)
        assert corr_plot.axes[0].get_title() == "Pearson Correlation (Top 20)"
        assert len(corr_plot.axes[0].patches) == 20  # Top 20 of 25


def test_plot_regression_function():
    data = DataFrame({"A": range(60000), "B": [1, 2, 3] * 20000})
    var_pair, reg_plot = plot_regression(data)

    assert var_pair == ("A", "B")
    assert isinstance(reg_plot, Figure)
    assert "Slope" in reg_plot.axes[0].get_title()

    # Check that a sample of size 50000 is taken for large datasets
    points = reg_plot.axes[0].collections[0].get_offsets().data
    assert len(points) == 50000


class TestPlotMultivariable:
    def test_without_numeric_pairs(self):
        data = MultiVariable(range(50))
        assert plot_multivariable(data) is None

    def test_with_numeric_pairs(self):
        data = MultiVariable([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        graphs = plot_multivariable(data)

        assert set(graphs.keys()) == {
            "correlation_heatmap",
            "regression_plots",
        }
        heatmap = graphs["correlation_heatmap"]
        reg_plots = list(graphs["regression_plots"].values())

        for graph in reg_plots + [heatmap]:
            assert isinstance(graph, BytesIO)
