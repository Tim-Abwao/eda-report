from io import BytesIO
from multiprocessing import Pool
from typing import Sequence, Tuple

import matplotlib as mpl
import numpy as np
from cycler import cycler
from matplotlib.colors import to_rgb
from matplotlib.figure import Figure
from pandas import Series
from scipy.stats import gaussian_kde, probplot
from tqdm import tqdm

from eda_report.multivariate import MultiVariable

# Matplotlib configuration
mpl.rc("figure", autolayout=True, dpi=150, figsize=(6.5, 4))
mpl.rc("font", family="serif")
mpl.rc("axes.spines", top=False, right=False)
mpl.rc("axes", titlesize=12, titleweight=500)
mpl.use("agg")  # use non-interactive matplotlib back-end

# Customize boxplots
mpl.rc("boxplot", patchartist=True, vertical=False)
mpl.rc("boxplot.medianprops", color="black")


def savefig(figure: Figure) -> BytesIO:
    """Saves the contents of a :class:`~matplotlib.figure.Figure` in PNG
    format, as bytes in a file-like object.

    This is a utility function helpful in by-passing the *filesystem*. Graphs
    are stored in :class:`~io.BytesIO` objects, and can then be read
    directly as *attributes*, thus allowing rapid in-memory access.

    Args:
        figure (matplotlib.figure.Figure): Graph content.

    Returns:
        io.BytesIO: A graph in PNG format as bytes.
    """
    graph = BytesIO()
    figure.savefig(graph, format="png")

    return graph


def set_custom_palette(color: str, num: int) -> None:
    """Create a custom colormap based on the specified `color`.

    Args:
        color (str): Valid matplotlib color specifier.
        num (int): Number of colors to generate.
    """
    color_rgb = to_rgb(color)
    color_array = np.linspace(color_rgb, (0.25, 0.25, 0.25), num=num)
    mpl.rc("axes", prop_cycle=cycler(color=color_array))


def box_plot(data: Series, *, label: str, hue: Series = None) -> Figure:
    """Get a boxplot from numeric values.
    Args:
        data (Series): Values to plot.
        label (str): A name for the `data`.
        hue (Series, optional): Values for grouping the `data`. Defaults to
            None.

    Returns:
        matplotlib.figure.Figure: Matplotlib figure with the box-plot.
    """
    data = data.dropna()
    fig = Figure()
    ax = fig.subplots()

    if hue is None:
        bplot = ax.boxplot(data, labels=[label], sym=".")
        ax.set_yticklabels("")
    else:
        groups = {key: group for key, group in data.groupby(hue)}
        bplot = ax.boxplot(groups.values(), labels=groups.keys(), sym=".")

    for idx, patch in enumerate(bplot["boxes"]):
        patch.set_facecolor(f"C{idx}")
        patch.set_alpha(0.75)

    ax.set_title(f"Box-plot of {label}")

    return fig


def kde_plot(data: Series, *, label: str, hue: Series = None) -> Figure:
    """Get a kde-plot from numeric values.

    Args:
        data (Series): Values to plot.
        label (str): A name for the `data`.
        hue (Series, optional): Values for grouping the `data`. Defaults to
            None.

    Returns:
        matplotlib.figure.Figure: Matplotlib figure with the kde-plot.
    """
    data = data.dropna()
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

    eval_points = np.linspace(*(data.agg([min, max])), num=len(data))
    if hue is None:
        kernel = gaussian_kde(data)
        density = kernel(eval_points)
        ax.plot(eval_points, density, label=label)
        ax.fill_between(eval_points, density, alpha=0.4)
    else:
        for key, _series in data.groupby(hue):
            kernel = gaussian_kde(_series)
            density = kernel(eval_points)
            ax.plot(eval_points, density, label=key, alpha=0.75)
            ax.fill_between(eval_points, density, alpha=0.25)

    ax.set_ylim(0)
    ax.legend()
    ax.set_title(f"Distribution plot of {label}")

    return fig


def prob_plot(data: Series, *, label: str, hue: Series = None) -> Figure:
    """Get a probability-plot from numeric values.

    Args:
        data (Series): Values to plot.
        label (str): A name for the `data`.
        hue (Series, optional): Values for grouping the `data`. Defaults to
            None.

    Returns:
        matplotlib.figure.Figure: Matplotlib figure with the kde-plot.
    """
    data = data.dropna()
    fig = Figure(figsize=(6.5, 4.5))
    ax = fig.subplots()
    probplot(data, fit=True, plot=ax)
    ax.lines[0].set_color("C0")
    ax.lines[1].set_color("k")
    ax.set_title(f"Probability plot of {label}")
    return fig


def bar_plot(data: Series, *, label: str) -> Figure:
    """Get a bar-plot from categorical values.

    Args:
        data (Series): Values to plot.
        label (str): A name for the `data`.

    Returns:
        matplotlib.figure.Figure: Matplotlib figure with the kde-plot.
    """
    data = data.dropna()
    fig = Figure()
    ax = fig.subplots()

    # Include no more than 10 of the most common values
    top_10 = data.value_counts().nlargest(10)
    ax.bar(top_10.index, top_10, alpha=0.8)
    if (num_unique := data.nunique()) > 10:
        ax.set_title(f"Bar-plot of {label} (Top 10 of {num_unique})")
    else:
        ax.set_title(f"Bar-plot of {label}")

    # Annotate bars
    for p in ax.patches:
        ax.annotate(
            f"{p.get_height():,.0f}",
            ha="center",
            size=8,
            xy=(p.get_x() + p.get_width() / 2, p.get_height() * 1.02),
        )

    return fig


def plot_variable(variable_and_hue: Tuple, hue=None) -> Sequence:
    """Get graphs (as PNG images) for a variable based on it's type."""
    variable, hue = variable_and_hue
    if variable.var_type == "numeric":
        graphs = [
            savefig(
                plot_func(data=variable.data, hue=hue, label=variable.name)
            )
            for plot_func in [box_plot, kde_plot, prob_plot]
        ]
    else:  # {"boolean", "categorical", "datetime"}:
        graphs = [savefig(bar_plot(data=variable.data, label=variable.name))]

    return variable.name, graphs


def plot_correlation(variables: MultiVariable) -> Figure:
    """Create a bar chart showing the top 20 most correlated variables.

    Returns:
        Figure: A bar-plot in PNG format as bytes.
    """
    pairs = list(variables.var_pairs)
    corr_data = (
        variables.correlation_df.unstack()  # get MultiIndex of cols
        .loc[pairs]  # select unique pairs
        .sort_values(key=abs)  # sort by magnitude
        .tail(20)  # select top 20
    )
    labels = corr_data.index.map(" vs ".join)

    fig = Figure(figsize=(7, 6.3))
    ax = fig.subplots()
    ax.barh(labels, corr_data)
    ax.set_xlim(-1, 1)
    ax.spines["left"].set_visible(False)
    ax.yaxis.set_visible(False)
    ax.axvline(0, 0, 1, color="#777")

    for p, label in zip(ax.patches, labels):
        p.set_alpha(abs(p.get_width()))
        p.set_edgecolor("#777")

        if p.get_width() < 0:
            p.set_facecolor("steelblue")
            ax.text(
                p.get_x(),
                p.get_y() + p.get_height() / 2,
                f"{p.get_width():,.2f} ({label})  ",
                size=8,
                ha="right",
                va="center",
            )
        else:
            p.set_facecolor("orangered")
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


def plot_regression(data) -> Figure:
    """Get a regression-plot and ecdf-plot for the provided column pair.

    Args:
        var_pair (Tuple[str, str]): Numeric column pair.

    Returns:
        io.BytesIO: The regression-plot and ecdf-plot as subplots, in PNG
        format.
    """
    fig = Figure(figsize=(5, 4.8))
    ax = fig.subplots()

    data = data.dropna()
    if len(data) > 50000:
        data = data.sample(50000)

    var1, var2 = data.columns
    x = data[var1]
    y = data[var2]
    slope, intercept = np.polyfit(x, y, deg=1)
    line_x = np.linspace(x.min(), x.max(), num=100)

    ax.scatter(x, y, s=40, alpha=0.7, edgecolors="#444")
    ax.plot(line_x, slope * line_x + intercept, color="#444", lw=2)
    ax.set_title(f"Slope: {slope:,.4f}\nIntercept: {intercept:,.4f}", size=11)
    ax.set_xlabel(var1)
    ax.set_ylabel(var2)

    return (var1, var2), savefig(fig)


def plot_multivariable(variables: MultiVariable):

    if hasattr(variables, "var_pairs"):
        paired_data_gen = (
            variables.data.loc[:, pair].dropna()
            for pair in variables.var_pairs
        )
        with Pool() as p:
            bivariate_regression_plots = dict(
                tqdm(
                    p.imap(plot_regression, paired_data_gen),
                    total=len(variables.var_pairs),
                    bar_format=(
                        "{desc} {percentage:3.0f}%|{bar:35}| "
                        "{n_fmt}/{total_fmt} pairs."
                    ),
                    desc="Bivariate analysis:",
                    dynamic_ncols=True,
                )
            )

        return {
            "correlation_heatmap": savefig(plot_correlation(variables)),
            "regression_plots": bivariate_regression_plots,
        }
    else:
        return None
