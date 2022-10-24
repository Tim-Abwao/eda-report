from io import BytesIO
from multiprocessing import Pool
from typing import Dict, Iterable, Optional, Sequence, Tuple, Union

import matplotlib as mpl
import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.figure import Figure
from scipy.stats import gaussian_kde, probplot
from tqdm import tqdm

from eda_report.multivariate import MultiVariable
from eda_report.validate import (
    validate_multivariate_input,
    validate_univariate_input,
)

# Matplotlib configuration
mpl.rc("figure", autolayout=True, dpi=150, figsize=(6.5, 4))
mpl.rc("font", family="serif")
mpl.rc("axes.spines", top=False, right=False)
mpl.rc("axes", titlesize=12, titleweight=500)
mpl.use("agg")  # use non-interactive matplotlib back-end

# Customize boxplots
mpl.rc("boxplot", patchartist=True, vertical=False)
mpl.rc("boxplot.medianprops", color="black")


def _savefig(figure: Figure) -> BytesIO:
    """Saves the contents of a :class:`~matplotlib.figure.Figure` in PNG
    format, as bytes in a file-like object.

    This is a utility function helpful in by-passing the *filesystem*. Graphs
    are stored in :class:`~io.BytesIO` objects, and can then be read
    directly as *attributes*, thus allowing rapid in-memory access when
    compiling the report.

    Args:
        figure (matplotlib.figure.Figure): Graph content.

    Returns:
        io.BytesIO: A graph in PNG format as bytes.
    """
    graph = BytesIO()
    figure.savefig(graph, format="png")

    return graph


def _get_color_shades_of(color: str, num: int = None) -> Sequence:
    """Obtain an array of `num` shades of the specified `color`.

    Args:
        color (str): The desired color.
        num (int): Desired number of color shades.
    """
    color_rgb = to_rgb(color)
    return np.linspace(color_rgb, (0.25, 0.25, 0.25), num=num)


def box_plot(
    data: Iterable,
    *,
    label: str,
    hue: Iterable = None,
    color: Union[str, Sequence] = None,
) -> Figure:
    """Get a box-plot from numeric values.

    Args:
        data (Iterable): Values to plot.
        label (str): A name for the `data`, shown in the title.
        hue (Iterable, optional): Values for grouping the `data`. Defaults to
            None.
        color (Union[str, Sequence]): A valid matplotlib color specifier.

    Returns:
        matplotlib.figure.Figure: Matplotlib figure with the box-plot.
    """
    original_data = validate_univariate_input(data)
    data = original_data.dropna()

    fig = Figure()
    ax = fig.subplots()

    if hue is None:
        bxplot = ax.boxplot(
            data,
            labels=[label],
            sym=".",
            boxprops=dict(facecolor=color, alpha=0.75),
        )
        ax.set_yticklabels("")
    else:
        hue = validate_univariate_input(hue)[original_data.notna()]
        groups = {key: series for key, series in data.groupby(hue)}
        bxplot = ax.boxplot(groups.values(), labels=groups.keys(), sym=".")

        if color is None:
            colors = [f"C{idx}" for idx in range(hue.nunique())]
        else:
            colors = _get_color_shades_of(color, hue.nunique())

        for patch, color in zip(bxplot["boxes"], reversed(colors)):
            patch.set_facecolor(color)
            patch.set_alpha(0.75)

    ax.set_title(f"Box-plot of {label}")

    return fig


def kde_plot(
    data: Iterable,
    *,
    label: str,
    hue: Iterable = None,
    color: Union[str, Sequence] = None,
) -> Figure:
    """Get a kde-plot from numeric values.

    Args:
        data (Iterable): Values to plot.
        label (str): A name for the `data`, shown in the title.
        hue (Iterable, optional): Values for grouping the `data`. Defaults to
            None.
        color (Union[str, Sequence]): A valid matplotlib color specifier.

    Returns:
        matplotlib.figure.Figure: Matplotlib figure with the kde-plot.
    """
    original_data = validate_univariate_input(data)
    data = original_data.dropna()

    fig = Figure()
    ax = fig.subplots()

    if len(data) < 2 or np.isclose(data.std(), 0):
        ax.text(
            x=0.08,
            y=0.45,
            s=(
                "[Could not plot kernel density estimate.\n "
                "Data is singular.]"
            ),
            color="#f72",
            size=14,
            weight=600,
        )
        return fig

    eval_points = np.linspace(data.min(), data.max(), num=len(data))
    if hue is None:
        kernel = gaussian_kde(data)
        density = kernel(eval_points)
        ax.plot(eval_points, density, label=label, color=color)
        ax.fill_between(eval_points, density, alpha=0.3, color=color)
    else:
        hue = validate_univariate_input(hue)[original_data.notna()]
        if color is None:
            colors = [f"C{idx}" for idx in range(hue.nunique())]
        else:
            colors = _get_color_shades_of(color, hue.nunique())

        for color, (key, series) in zip(colors, data.groupby(hue)):
            kernel = gaussian_kde(series)
            density = kernel(eval_points)
            ax.plot(eval_points, density, label=key, alpha=0.75, color=color)
            ax.fill_between(eval_points, density, alpha=0.25, color=color)

    ax.set_ylim(0)
    ax.legend()
    ax.set_title(f"Density plot of {label}")

    return fig


def prob_plot(
    data: Iterable,
    *,
    label: str,
    marker_color: Union[str, Sequence] = "C0",
    line_color: Union[str, Sequence] = "#222",
) -> Figure:
    """Get a probability-plot from numeric values.

    Args:
        data (Iterable): Values to plot.
        label (str): A name for the `data`, shown in the title.
        marker_color (Union[str, Sequence]): Color for the plotted points.
            Defaults to "C0".
        line_color (Union[str, Sequence]): Color for the line of best fit.
            Defaults to "#222".

    Returns:
        matplotlib.figure.Figure: Matplotlib figure with the probability-plot.
    """
    original_data = validate_univariate_input(data)
    data = original_data.dropna()

    fig = Figure(figsize=(6.5, 4.5))
    ax = fig.subplots()
    probplot(data, fit=True, plot=ax)
    ax.lines[0].set_color(marker_color)
    ax.lines[1].set_color(line_color)
    ax.set_title(f"Probability plot of {label}")

    return fig


def bar_plot(
    data: Iterable, *, label: str, color: Union[str, Sequence] = None
) -> Figure:
    """Get a bar-plot from a sequence of values.

    Args:
        data (Iterable): Values to plot.
        label (str): A name for the `data`, shown in the title.
        color (Union[str, Sequence]): A valid matplotlib color specifier.

    Returns:
        matplotlib.figure.Figure: Matplotlib figure with the bar-plot.
    """
    original_data = validate_univariate_input(data)
    data = original_data.dropna()

    fig = Figure()
    ax = fig.subplots()

    # Include no more than 10 of the most common values
    top_10 = data.value_counts().nlargest(10)
    bars = ax.bar(top_10.index, top_10, alpha=0.8, color=color)
    ax.bar_label(bars, labels=[f"{x:,.0f}" for x in top_10], padding=2)

    if (num_unique := data.nunique()) > 10:
        title = f"Bar-plot of {label} (Top 10 of {num_unique})"
    else:
        title = f"Bar-plot of {label}"
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=90)  # Improve visibility of long labels

    return fig


def _plot_variable(variables_hue_and_color: Tuple) -> Tuple:
    """Helper function to concurrently plot variables in a multiprocessing
    Pool.

    Args:
        variables_hue_and_color (Tuple): A variable, hue data and the desired
            theme.

    Returns:
        Tuple: `variable`s name, and graphs in a dict.
    """
    variable, hue, color = variables_hue_and_color
    if variable.var_type == "numeric":
        graphs = {
            "box_plot": _savefig(
                box_plot(
                    data=variable.data,
                    hue=hue,
                    label=variable.name,
                    color=color,
                )
            ),
            "kde_plot": _savefig(
                kde_plot(
                    data=variable.data,
                    hue=hue,
                    label=variable.name,
                    color=color,
                )
            ),
            "prob_plot": _savefig(
                prob_plot(
                    data=variable.data, label=variable.name, marker_color=color
                )
            ),
        }
    else:  # {"boolean", "categorical", "datetime"}:
        graphs = {
            "bar_plot": _savefig(
                bar_plot(data=variable.data, label=variable.name, color=color)
            )
        }

    return variable.name, graphs


def plot_correlation(
    variables: Iterable,
    max_pairs: int = 20,
    color_pos: Union[str, Sequence] = "orangered",
    color_neg: Union[str, Sequence] = "steelblue",
) -> Figure:
    """Create a bar chart showing the top ``max_pairs`` most correlated
    variables.

    Args:
        variables (Iterable): 2-dimensional data.
        max_pairs (int): The maximum number of numeric pairs to include in the
            plot. Defaults to 20.
        color_pos (Union[str, Sequence]): Color for positive correlation bars.
            Defaults to "orangered".
        color_neg (Union[str, Sequence]): Color for negative correlation bars.
            Defaults to "steelblue".

    Returns:
        matplotlib.figure.Figure: A bar-plot of correlation data.
    """
    if not isinstance(variables, MultiVariable):
        variables = MultiVariable(variables)

    pairs = list(variables.var_pairs)
    corr_data = (
        variables.correlation_df.unstack()  # get MultiIndex of cols
        .loc[pairs]  # select unique pairs
        .sort_values(key=abs)  # sort by magnitude
        .tail(max_pairs)  # select top `max_pairs` (default 20)
    )
    labels = corr_data.index.map(" vs ".join)

    fig = Figure(figsize=(7, 6.3))
    ax = fig.subplots()
    ax.barh(labels, corr_data, edgecolor="#777")
    ax.set_xlim(-1, 1)
    ax.spines["left"].set_position("zero")
    ax.yaxis.set_visible(False)  # hide y-axis labels

    for p, label in zip(ax.patches, labels):
        p.set_alpha(abs(p.get_width()))

        if p.get_width() < 0:
            p.set_facecolor(color_neg)
            ax.text(
                p.get_x(),
                p.get_y() + p.get_height() / 2,
                f"{p.get_width():,.2f} ({label})  ",
                size=8,
                ha="right",
                va="center",
            )
        else:
            p.set_facecolor(color_pos)
            ax.text(
                p.get_x(),
                p.get_y() + p.get_height() / 2,
                f"  {p.get_width():,.2}  ({label})",
                size=8,
                ha="left",
                va="center",
            )

    ax.set_title(f"Pearson Correlation (Top {len(corr_data)})")

    return fig


def regression_plot(
    x: Iterable,
    y: Iterable,
    labels: Tuple[str, str],
    color: Union[str, Sequence] = None,
) -> Figure:
    """Get a regression-plot from the provided pair of values.

    Args:
        x (Iterable): Numeric values.
        y (Iterable): Numeric values.
        labels (Tuple[str, str]): Names for `x` and `y` respectively, shown in
            axis labels.
        color (Union[str, Sequence]): A valid matplotlib color specifier.

    Returns:
        matplotlib.figure.Figure: Matplotlib figure with the regression-plot.
    """
    var1, var2 = labels
    # Convert to DataFrame
    data = validate_multivariate_input({var1: x, var2: y}).dropna()

    if len(data) > 50000:
        data = data.sample(50000)

    fig = Figure(figsize=(5, 5))
    ax = fig.subplots()
    x = data[var1]
    y = data[var2]
    slope, intercept = np.polyfit(x, y, deg=1)
    line_x = np.linspace(x.min(), x.max(), num=100)

    ax.scatter(x, y, s=40, alpha=0.7, color=color, edgecolors="#444")
    ax.plot(line_x, slope * line_x + intercept, color="#444", lw=2)
    ax.set_title(
        f"Slope: {slope:,.4f}\nIntercept: {intercept:,.4f}\n"
        + f"Correlation: {x.corr(y):.4f}",
        size=11,
    )
    ax.set_xlabel(var1)
    ax.set_ylabel(var2)

    return fig


def _plot_regression(data_and_color: Tuple) -> Tuple:
    """Helper function to plot regression plots concurrently.

    Args:
        data_and_color (Tuple): A pair of numeric values.

    Returns:
        Tuple: Names for the pair of values, and a figure with the regression
        plot.
    """
    data, color = data_and_color
    var1, var2 = data.columns
    fig = regression_plot(
        x=data[var1], y=data[var2], labels=(var1, var2), color=color
    )
    return (var1, var2), fig


def _plot_multivariable(
    variables: MultiVariable, color: str = None
) -> Optional[Dict]:
    """Concurrently plot regression plots in a multiprocessing Pool.

    Args:
        variables (MultiVariable): Bi-variate analysis results.
        color (str, optional): The color to apply to the graphs.

    Returns:
        Optional[Dict]: A dictionary with a correlation plot and regression
        plots.
    """
    if hasattr(variables, "var_pairs"):
        var_pairs = list(variables.var_pairs)

        if len(variables.var_pairs) > 50:
            # Take the top 50 var_pairs by magnitude of correlation.
            # 50 var_pairs == 25+ pages
            # 20 numeric columns == upto 190 pairs (95+ pages).
            var_pairs = (
                variables.correlation_df.unstack()[var_pairs]
                .sort_values(key=abs)
                .tail(50)
                .index
            )
        with Pool() as p:
            paired_data_gen = [
                (variables.data.loc[:, pair], color) for pair in var_pairs
            ]
            bivariate_regression_plots = dict(
                tqdm(
                    p.imap(_plot_regression, paired_data_gen),
                    total=len(var_pairs),
                    bar_format=(
                        "{desc} {percentage:3.0f}%|{bar:35}| "
                        "{n_fmt}/{total_fmt} pairs."
                    ),
                    desc="Bivariate analysis:",
                    dynamic_ncols=True,
                )
            )

        return {
            "correlation_plot": _savefig(plot_correlation(variables)),
            "regression_plots": {
                var_pair: _savefig(plot)
                for var_pair, plot in bivariate_regression_plots.items()
            },
        }
    else:
        return None
