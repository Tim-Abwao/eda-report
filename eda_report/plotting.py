from io import BytesIO
from multiprocessing import Pool
from typing import Dict, Iterable, Optional, Sequence, Tuple, Union

import matplotlib as mpl
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import to_rgb
from matplotlib.figure import Figure
from scipy.stats import gaussian_kde, probplot
from tqdm import tqdm

from eda_report._validate import _validate_dataset, _validate_univariate_input
from eda_report.bivariate import Dataset

# Matplotlib configuration
GENERAL_RC_PARAMS = {
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 12,
    "axes.titleweight": 500,
    "figure.autolayout": True,
    "figure.figsize": (5.6, 3.5),
    "font.family": "serif",
    "savefig.dpi": 120,
}
# Customize box-plots
BOXPLOT_RC_PARAMS = {
    **GENERAL_RC_PARAMS,
    "boxplot.medianprops.color": "black",
    "boxplot.patchartist": True,
    "boxplot.vertical": False,
}
# Customize correlation-plots
CORRPLOT_RC_PARAMS = {**GENERAL_RC_PARAMS, "figure.figsize": (7, 6.3)}
# Customize regression-plots
REGPLOT_RC_PARAMS = {**GENERAL_RC_PARAMS, "figure.figsize": (5.2, 5)}


@mpl.rc_context(GENERAL_RC_PARAMS)
def _savefig(figure: Figure) -> BytesIO:
    """Saves the contents of a :class:`~matplotlib.figure.Figure` in PNG
    format, as bytes in a file-like object. This allows rapid in-memory 
    access when compiling the report.

    Args:
        figure (matplotlib.figure.Figure): Graph content.

    Returns:
        io.BytesIO: A graph in PNG format as bytes.
    """
    graph = BytesIO()
    figure.savefig(graph, format="png")
    return graph


def _get_or_validate_axes(ax: Axes = None) -> Axes:
    """Create or validate an Axes instance.

    Args:
        ax (matplotlib.axes.Axes, optional): Axes instance. Defaults to None.

    Raises:
        TypeError: If `ax` is not an Axes instance.

    Returns:
        Axes: Axes instance.
    """
    if ax is None:
        return Figure().subplots()
    elif isinstance(ax, Axes):
        return ax
    else:
        raise TypeError(f"Invalid input for 'ax': {type(ax)}")


def _get_color_shades_of(color: str, num: int = None) -> Sequence:
    """Obtain an array with `num` shades of the specified `color`.

    Args:
        color (str): The desired color.
        num (int): Desired number of color shades.

    Returns:
        Sequence: Array of RGB colors.
    """
    color_rgb = to_rgb(color)
    return np.linspace(color_rgb, (0.25, 0.25, 0.25), num=num)


@mpl.rc_context(BOXPLOT_RC_PARAMS)
def box_plot(
    data: Iterable,
    *,
    label: str,
    hue: Iterable = None,
    color: Union[str, Sequence] = None,
    ax: Axes = None,
) -> Axes:
    """Get a box-plot from numeric values.

    Args:
        data (Iterable): Values to plot.
        label (str): A name for the ``data``, shown in the title.
        hue (Iterable, optional): Values for grouping the ``data``. Defaults to
            None.
        color (Union[str, Sequence]): A valid matplotlib color specifier.
        ax (matplotlib.axes.Axes, optional): Axes instance. Defaults to None.

    Returns:
        matplotlib.axes.Axes: Matplotlib axes with the box-plot.
    """
    original_data = _validate_univariate_input(data)
    data = original_data.dropna()
    ax = _get_or_validate_axes(ax)
    if hue is None:
        bxplot = ax.boxplot(
            data,
            labels=[label],
            sym=".",
            boxprops=dict(facecolor=color, alpha=0.75),
        )
        ax.set_yticklabels("")
    else:
        hue = _validate_univariate_input(hue)[original_data.notna()]
        groups = {key: sub_series for key, sub_series in data.groupby(hue)}
        bxplot = ax.boxplot(groups.values(), labels=groups.keys(), sym=".")

        if color is None:
            colors = [f"C{idx}" for idx in range(hue.nunique())]
        else:
            colors = _get_color_shades_of(color, hue.nunique())

        for patch, color in zip(bxplot["boxes"], reversed(colors)):
            patch.set_facecolor(color)
            patch.set_alpha(0.75)

        if hue.name is not None:
            ax.set_ylabel(f"{hue.name}".title())

    ax.set_title(f"Box-plot of {label}")
    return ax


@mpl.rc_context(GENERAL_RC_PARAMS)
def kde_plot(
    data: Iterable,
    *,
    label: str,
    hue: Iterable = None,
    color: Union[str, Sequence] = None,
    ax: Axes = None,
) -> Axes:
    """Get a kde-plot from numeric values.

    Args:
        data (Iterable): Values to plot.
        label (str): A name for the ``data``, shown in the title.
        hue (Iterable, optional): Values for grouping the ``data``. Defaults to
            None.
        color (Union[str, Sequence]): A valid matplotlib color specifier.
        ax (matplotlib.axes.Axes, optional): Axes instance. Defaults to None.

    Returns:
        matplotlib.axes.Axes: Matplotlib axes with the kde-plot.
    """
    original_data = _validate_univariate_input(data)
    data = original_data.dropna()
    ax = _get_or_validate_axes(ax)
    if len(data) < 2 or np.isclose(data.std(), 0):
        msg = "[Could not plot kernel density estimate.\n Data is singular.]"
        ax.text(x=0.08, y=0.45, s=msg, color="#f72", size=14, weight=600)
        return ax

    eval_points = np.linspace(data.min(), data.max(), num=len(data))
    if hue is None:
        kernel = gaussian_kde(data)
        density = kernel(eval_points)
        ax.plot(eval_points, density, label=label, color=color)
        ax.fill_between(eval_points, density, alpha=0.3, color=color)
    else:
        hue = _validate_univariate_input(hue)[original_data.notna()]
        if color is None:
            colors = [f"C{idx}" for idx in range(hue.nunique())]
        else:
            colors = _get_color_shades_of(color, hue.nunique())

        for color, (key, series) in zip(colors, data.groupby(hue)):
            kernel = gaussian_kde(series)
            density = kernel(eval_points)
            ax.plot(eval_points, density, label=key, alpha=0.75, color=color)
            ax.fill_between(eval_points, density, alpha=0.25, color=color)

        if hue.name is not None:
            ax.legend(title=f"{hue.name}".title())

    ax.set_xlabel(label)
    ax.set_ylim(0)
    ax.set_title(f"Density plot of {label}")
    return ax


@mpl.rc_context(REGPLOT_RC_PARAMS)
def prob_plot(
    data: Iterable,
    *,
    label: str,
    marker_color: Union[str, Sequence] = "C0",
    line_color: Union[str, Sequence] = "#222",
    ax: Axes = None,
) -> Axes:
    """Get a probability-plot from numeric values.

    Args:
        data (Iterable): Values to plot.
        label (str): A name for the ``data``, shown in the title.
        marker_color (Union[str, Sequence]): Color for the plotted points.
            Defaults to "C0".
        line_color (Union[str, Sequence]): Color for the line of best fit.
            Defaults to "#222".
        ax (matplotlib.axes.Axes, optional): Axes instance. Defaults to None.

    Returns:
        matplotlib.axes.Axes: Matplotlib axes with the probability-plot.
    """
    original_data = _validate_univariate_input(data)
    data = original_data.dropna()
    ax = _get_or_validate_axes(ax)
    probplot(data, fit=True, plot=ax)
    ax.lines[0].set_color(marker_color)
    ax.lines[1].set_color(line_color)
    ax.set_xlabel("Theoretical Quantiles (Normal)")
    ax.set_title(f"Probability plot of {label}")
    return ax


@mpl.rc_context(GENERAL_RC_PARAMS)
def bar_plot(
    data: Iterable,
    *,
    label: str,
    color: Union[str, Sequence] = None,
    ax: Axes = None,
) -> Axes:
    """Get a bar-plot from a sequence of values.

    Args:
        data (Iterable): Values to plot.
        label (str): A name for the ``data``, shown in the title.
        color (Union[str, Sequence]): A valid matplotlib color specifier.
        ax (matplotlib.axes.Axes, optional): Axes instance. Defaults to None.

    Returns:
        matplotlib.axes.Axes: Matplotlib axes with the bar-plot.
    """
    original_data = _validate_univariate_input(data)
    data = original_data.dropna()
    ax = _get_or_validate_axes(ax)
    # Include no more than 10 of the most common values
    top_10 = data.value_counts().nlargest(10)
    bars = ax.bar(top_10.index.map(str), top_10, alpha=0.8, color=color)
    ax.bar_label(bars, labels=[f"{x:,.0f}" for x in top_10], padding=2)
    if (num_unique := data.nunique()) > 10:
        title = f"Bar-plot of {label} (Top 10 of {num_unique})"
    else:
        title = f"Bar-plot of {label}"
    ax.set_title(title)
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=90)  # Improve visibility for long labels
    return ax


def _plot_variable(variable_data_hue_and_color: Tuple) -> Tuple:
    """Helper function to concurrently plot variables in a multiprocessing
    Pool.

    Args:
        variable_data_hue_and_color (Tuple): A variable, plot data, hue data
            and the desired plot color.

    Returns:
        Tuple: `variable`s name, and graphs in a dict.
    """
    variable, data, hue, color = variable_data_hue_and_color
    if variable.var_type == "numeric":
        plots = {
            "box_plot": box_plot(
                data=data, hue=hue, label=variable.name, color=color
            ),
            "kde_plot": kde_plot(
                data=data, hue=hue, label=variable.name, color=color
            ),
            "prob_plot": prob_plot(
                data, label=variable.name, marker_color=color
            ),
        }
    else:  # {"boolean", "categorical", "datetime", "numeric (<=10 levels)"}
        plots = {"bar_plot": bar_plot(data, label=variable.name, color=color)}

    graph_images = {name: _savefig(ax.figure) for name, ax in plots.items()}
    return variable.name, graph_images


@mpl.rc_context(CORRPLOT_RC_PARAMS)
def plot_correlation(
    variables: Iterable,
    max_pairs: int = 20,
    color_pos: Union[str, Sequence] = "orangered",
    color_neg: Union[str, Sequence] = "steelblue",
    ax: Axes = None,
) -> Axes:
    """Create a bar chart showing the top ``max_pairs`` most correlated
    variables. Bars are annotated with variable pairs and their respective
    Pearson correlation coefficients.

    Args:
        variables (Iterable): 2-dimensional numeric data.
        max_pairs (int): The maximum number of numeric pairs to include in the
            plot. Defaults to 20.
        color_pos (Union[str, Sequence]): Color for positive correlation bars.
            Defaults to "orangered".
        color_neg (Union[str, Sequence]): Color for negative correlation bars.
            Defaults to "steelblue".
        ax (matplotlib.axes.Axes, optional): Axes instance. Defaults to None.

    Returns:
        matplotlib.axes.Axes: A bar-plot of correlation data.
    """
    if not isinstance(variables, Dataset):
        variables = Dataset(variables)

    if variables._correlation_values is None:
        return None

    # Show at most `max_pairs` numeric pairs.
    pairs_to_show = variables._correlation_values[:max_pairs]
    # Reverse items so largest values appear at the top.
    corr_data = dict(reversed(pairs_to_show))
    labels = [" vs ".join(pair) for pair in corr_data.keys()]
    ax = _get_or_validate_axes(ax)
    ax.barh(labels, corr_data.values(), edgecolor="#222", linewidth=0.5)
    ax.set_xlim(-1.1, 1.1)
    ax.spines["left"].set_position("zero")  # Place y-axis spine at x=0
    ax.yaxis.set_visible(False)  # Hide y-axis labels

    for p, label in zip(ax.patches, labels):
        p.set_alpha(min(1, abs(p.get_width()) + 0.1))
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
                f"  {p.get_width():,.2} ({label})",
                size=8,
                ha="left",
                va="center",
            )

    ax.set_title(f"Pearson Correlation (Top {len(corr_data)})")
    return ax


@mpl.rc_context(REGPLOT_RC_PARAMS)
def regression_plot(
    x: Iterable,
    y: Iterable,
    labels: Tuple[str, str],
    marker_color: Union[str, Sequence] = "C0",
    line_color: Union[str, Sequence] = "#444",
    ax: Axes = None,
) -> Axes:
    """Get a regression-plot from the provided pair of numeric values.

    Args:
        x (Iterable): Numeric values.
        y (Iterable): Numeric values.
        labels (Tuple[str, str]): Names for `x` and `y` respectively, shown in
            axis labels.
        marker_color (Union[str, Sequence]): Color for the plotted points.
            Defaults to "C0".
        line_color (Union[str, Sequence]): Color for the line of best fit.
            Defaults to "#444".
        ax (matplotlib.axes.Axes, optional): Axes instance. Defaults to None.

    Returns:
        matplotlib.axes.Axes: Matplotlib axes with the regression-plot.
    """
    var1, var2 = labels
    data = _validate_dataset({var1: x, var2: y}).dropna()
    if len(data) > 50000:
        data = data.sample(50000)

    ax = _get_or_validate_axes(ax)
    x = data[var1]
    y = data[var2]
    slope, intercept = np.polyfit(x, y, deg=1)
    ax.scatter(x, y, s=40, alpha=0.7, color=marker_color, edgecolors="#444")
    reg_line_x = np.linspace(x.min(), x.max(), num=20)
    reg_line_y = slope * reg_line_x + intercept
    ax.plot(reg_line_x, reg_line_y, color=line_color, lw=2)
    ax.set_title(
        f"Slope: {slope:,.4f}\nIntercept: {intercept:,.4f}\n"
        + f"Correlation: {x.corr(y):.4f}",
        size=11,
    )
    ax.set_xlabel(var1)
    ax.set_ylabel(var2)
    return ax


def _plot_regression(data_and_color: Tuple) -> Tuple:
    """Helper function to plot regression-plots concurrently.

    Args:
        data_and_color (Tuple): Dataframe, and desired marker-color.

    Returns:
        Tuple: Names for the variable pair, and axes with the regression
        plot.
    """
    data, color = data_and_color
    var1, var2 = data.columns
    ax = regression_plot(
        x=data[var1], y=data[var2], labels=(var1, var2), marker_color=color
    )
    return (var1, var2), ax


def _plot_dataset(variables: Dataset, color: str = None) -> Optional[Dict]:
    """Concurrently plot regression-plots in a multiprocessing Pool.

    Args:
        variables (Dataset): Bi-variate analysis results.
        color (str, optional): The color to apply to the graphs.

    Returns:
        Optional[Dict]: A dictionary with a correlation plot and regression
        plots.
    """
    if variables._correlation_values is None:
        return None
    else:
        # Take the top 20 pairs by magnitude of correlation.
        # 20 var_pairs ≈ 10+ pages in report document
        # 20 numeric columns == 190 var_pairs ≈ 95+ pages.
        pairs_to_include = [
            pair for pair, _ in variables._correlation_values[:20]
        ]
        with Pool() as p:
            paired_data = [
                (variables.data.loc[:, pair], color)
                for pair in pairs_to_include
            ]
            bivariate_regression_plots = dict(
                tqdm(
                    # Plot in parallel processes
                    p.imap(_plot_regression, paired_data),
                    # Progress-bar options
                    total=len(pairs_to_include),
                    bar_format=(
                        "{desc} {percentage:3.0f}%|{bar:35}| "
                        "{n_fmt}/{total_fmt} pairs."
                    ),
                    desc="Bivariate analysis:",
                    dynamic_ncols=True,
                )
            )
        return {
            "correlation_plot": _savefig(plot_correlation(variables).figure),
            "regression_plots": {
                var_pair: _savefig(plot.figure)
                for var_pair, plot in bivariate_regression_plots.items()
            },
        }
