from collections.abc import Iterable
from io import BytesIO
from multiprocessing import Pool
from typing import Dict, Optional, Sequence, Tuple

import matplotlib as mpl
import numpy as np
import seaborn as sns
from cycler import cycler
from matplotlib.colors import to_rgb
from matplotlib.figure import Figure
from pandas import Series
from scipy.stats import gaussian_kde, probplot
from tqdm import tqdm

from eda_report.multivariate import MultiVariable
from eda_report.univariate import Variable
from eda_report.validate import validate_univariate_input

# Matplotlib configuration
mpl.rc("figure", autolayout=True, dpi=150, figsize=(6.5, 4))
mpl.rc("font", family="serif")
mpl.rc("axes.spines", top=False, right=False)
mpl.rc("axes", titlesize=12, titleweight=500)
mpl.use("agg")  # use non-interactive matplotlib back-end

# Customize boxplots
mpl.rc("boxplot", notch=True, patchartist=True, vertical=False)
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


class BasePlot:
    """Defines general plot settings, such as the the color palette and hue.

    Args:
        graph_color (str, optional): The color to apply to the generated
            graphs. Defaults to "cyan".
        hue (Iterable, optional): Data to use to group values. Defaults to
            None.
    """

    def __init__(
        self, *, graph_color: str = "cyan", hue: Iterable = None
    ) -> None:
        self.GRAPH_COLOR = graph_color
        self.HUE = validate_univariate_input(hue)


class UnivariatePlots(BasePlot):
    """Plots a collection of :class:`~eda_report.univariate.Variable`
    instances:

    - *Box-plots*, *dist-plots* and *normal-probability-plots* for
      numeric variables.
    - *Bar-plots* for categorical variables.

    Args:
        variables (Sequence[Variable]): List of variables to plot.
        graph_color (str, optional): The color to apply to the generated
            graphs. Defaults to "cyan".
        hue (pandas.Series, optional): Data to use to group values.
            Defaults to None.

    Attributes:
        graphs (Dict[str, BytesIO]): A dictionary of graphs, with graph names
           as keys and file-objects containing plotted graphs as values.
    """

    def __init__(
        self,
        variables: Sequence[Variable],
        *,
        graph_color: str = "cyan",
        hue: Series = None,
    ) -> None:
        super().__init__(graph_color=graph_color, hue=hue)
        self.variables = variables
        self.graphs = self._get_univariate_graphs()

    def _plot_box(self, variable: Variable) -> BytesIO:
        """Create a boxplot from a numeric variable.

        Args:
            variable (eda_report.univariate.Variable): The data to plot.

        Returns:
            io.BytesIO: The boxplot in PNG format.
        """
        fig = Figure()
        ax = fig.subplots()

        if self.HUE is None:
            bplot = ax.boxplot(variable.data, labels=[variable.name], sym=".")
            ax.set_yticklabels("")
        else:
            groups = {
                key: group for key, group in variable.data.groupby(self.HUE)
            }
            bplot = ax.boxplot(groups.values(), labels=groups.keys(), sym=".")

        for idx, patch in enumerate(bplot['boxes']):
            patch.set_facecolor(f"C{idx}")
            patch.set_alpha(.75)

        ax.set_title(f"Box-plot of {variable.name}")

        return savefig(fig)

    def _plot_kde(self, variable: Variable) -> BytesIO:
        """Get a kde-plot for a numeric variable.

        Args:
            variable (eda_report.univariate.Variable): The data to plot.

        Returns:
            io.BytesIO: The kde-plot in PNG format.
        """
        fig = Figure()
        ax = fig.subplots()
        fig = mpl.figure.Figure(figsize=(6.5, 4))
        ax = fig.subplots()

        if len(variable.data) < 2 or np.isclose(variable.data.std(), 0):
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
            return savefig(fig)

        eval_points = np.linspace(
            *(variable.data.agg([min, max])), num=len(variable.data)
        )

        if self.HUE is None:
            kernel = gaussian_kde(variable.data)
            density = kernel(eval_points)
            ax.plot(eval_points, density, label=variable.name)
            ax.fill_between(eval_points, density, alpha=0.4)
        else:
            for key, data in variable.data.groupby(self.HUE):
                kernel = gaussian_kde(data)
                density = kernel(eval_points)
                ax.plot(eval_points, density, label=key, alpha=0.75)
                ax.fill_between(eval_points, density, alpha=0.25)

        ax.set_ylim(0)
        ax.legend()
        ax.set_title(f"Distribution plot of {variable.name}")

        return savefig(fig)

    def _plot_prob(self, variable: Variable) -> BytesIO:
        """Get a probability plot for a numeric variable.

        Args:
            variable (eda_report.univariate.Variable): The data to plot.

        Returns:
            io.BytesIO: The probability plot in PNG.
        """
        fig = Figure(figsize=(6.5, 4.5))
        ax = fig.subplots()
        probplot(variable.data, fit=True, plot=ax)
        ax.lines[0].set_color("C0")
        ax.lines[1].set_color("k")
        ax.set_title(f"Probability plot of {variable.name}")
        return savefig(fig)

    def _plot_bar(self, variable: Variable) -> BytesIO:
        """Get a barplot for a categorical, boolean or datetime variable.

        Args:
            variable (eda_report.univariate.Variable): The data to plot.

        Returns:
            io.BytesIO: The barplot in PNG format.
        """
        fig = Figure()
        ax = fig.subplots()

        # Include no more than 10 of the most common values
        top_10 = variable.data.value_counts().nlargest(10)
        sns.barplot(
            x=list(top_10.index),
            y=top_10,
            ax=ax,
            palette=f"dark:{self.GRAPH_COLOR}_r",
        )
        ax.tick_params(axis="x", rotation=90)

        if (num_unique := variable.num_unique) > 10:
            ax.set_title(
                f"Bar-plot of {variable.name} (Top 10 of {num_unique})"
            )
        else:
            ax.set_title(f"Bar-plot of {variable.name}")

        # Annotate bars
        for p in ax.patches:
            ax.annotate(
                f"{p.get_height():,.0f}",
                ha="center",
                size=8,
                xy=(p.get_x() + p.get_width() / 2, p.get_height() * 1.02),
            )

        return savefig(fig)

    def _plot_variable(self, variable: Variable) -> Tuple[str, dict]:
        """Plot graphs based on the ``Variable`` type.

        For **numeric** variables, a *box-plot*, *dist-plot* and *probability
        plot* are produced.

        For **categorical**, **boolean** or **datetime** objects, only a *bar
        plot* is produced.

        Args:
            variable (eda_report.univariate.Variable): The data to plot.

        Returns:
            Tuple[str, Dict]: The variable's name, and a dictionary of its
            graphs.
        """
        if variable.var_type == "numeric":
            graphs = {
                "box_plot": self._plot_box(variable),
                "kde_plot": self._plot_dist(variable),
                "prob_plot": self._plot_prob(variable),
            }
        else:  # {"boolean", "categorical", "datetime"}:
            graphs = {"bar_plot": self._plot_bar(variable)}

        return variable.name, graphs

    def _get_univariate_graphs(self) -> Dict[str, Dict]:
        """Concurrently plot graphs for the variables present.

        Returns:
            Dict[str, Dict]: Variable names as keys, and their graphs as
            nested dictionaries.
        """
        with Pool() as p:
            univariate_graphs = dict(
                tqdm(
                    # Plot variables in parallel processes
                    p.imap(self._plot_variable, self.variables),
                    # Progress-bar options
                    total=len(self.variables),
                    bar_format=(
                        "{desc} {percentage:3.0f}%|{bar:35}| "
                        "{n_fmt}/{total_fmt}"
                    ),
                    desc="Plot variables:    ",
                    dynamic_ncols=True,
                )
            )
        return univariate_graphs


class BivariatePlots(BasePlot):
    """Plots instances of :class:`~eda_report.multivariate.MultiVariable`.

    Produces a *correlation heatmap*, *regression-plots* and *ecdf-plots*, if
    2 or more numeric columns are present, with more than 5% of their values
    being unique.

    Args:
        variables (MultiVariable): The data to plot.
        graph_color (str, optional): The color to apply to the generated
            graphs. Defaults to "cyan".
        hue (pandas.Series, optional): Data to use to group values.
            Defaults to None.

    Attributes:
        graphs (Dict[str, io.BytesIO]):
            A dictionary of graphs, with graph names as keys, and file-objects
            containing the plotted graphs as values.

            Bi-variate regression-plots are further nested in a dict of
            :class:`~io.BytesIO` objects, with tuples (col_i, col_j) as keys.
    """

    def __init__(
        self,
        variables: MultiVariable,
        *,
        graph_color: str = "cyan",
        hue: Series = None,
    ) -> None:
        super().__init__(graph_color=graph_color, hue=hue)
        self.variables = variables
        self.graphs = self._plot_graphs()

    def _plot_graphs(self) -> Optional[Dict]:
        """Get a heatmap of the correlation in all numeric columns, and
        regression-plots & ecdf-plots of numeric column pairs.

        Returns:
            Optional[Dict]: A dictionary with the correlation heatmap and
            regression + ECDF subplots.
        """
        if hasattr(self.variables, "var_pairs"):
            with Pool() as p:
                bivariate_regression_plots = dict(
                    tqdm(
                        p.imap(
                            self._regression_plot, self.variables.var_pairs
                        ),
                        total=len(self.variables.var_pairs),
                        bar_format=(
                            "{desc} {percentage:3.0f}%|{bar:35}| "
                            "{n_fmt}/{total_fmt} pairs."
                        ),
                        desc="Bivariate analysis:",
                        dynamic_ncols=True,
                    )
                )

            return {
                "correlation_heatmap": self._plot_correlation_heatmap(),
                "regression_plots": bivariate_regression_plots,
            }
        else:
            return None

    def _plot_correlation_heatmap(self) -> BytesIO:
        """Get a heatmap of the correlation among all numeric columns.

        Returns:
            io.BytesIO: The heatmap in PNG format as bytes.
        """
        fig = Figure(figsize=(7, 7))
        ax = fig.subplots()

        sns.heatmap(
            self.variables.correlation_df,
            annot=True,
            ax=ax,
            center=0,
            cmap="coolwarm",
            linewidths=2,
            mask=np.triu(self.variables.correlation_df),
            square=True,
            yticklabels=True,
        )
        ax.tick_params(rotation=45)
        fig.suptitle("Correlation in Numeric Columns", size=15)

        return savefig(fig)

    def _regression_plot(self, var_pair: Tuple[str, str]) -> BytesIO:
        """Get a regression-plot and ecdf-plot for the provided column pair.

        Args:
            var_pair (Tuple[str, str]): Numeric column pair.

        Returns:
            io.BytesIO: The regression-plot and ecdf-plot as subplots, in PNG
            format.
        """
        fig = Figure(figsize=(8.2, 4))
        ax1, ax2 = fig.subplots(nrows=1, ncols=2)
        var1, var2 = var_pair
        sns.regplot(
            x=var1,
            y=var2,
            data=self.variables.data,
            ax=ax1,
            color=self.GRAPH_COLOR,
        )

        pair_data = self.variables.data.loc[:, [var1, var2]]
        normalized_data = (pair_data - pair_data.mean()) / pair_data.std()
        sns.ecdfplot(
            data=normalized_data, ax=ax2, palette=f"dark:{self.GRAPH_COLOR}_r"
        )
        ax1.set_title(f"Regression-plot - {var1} vs {var2}".title(), size=9)
        ax2.set_title("Empirical Cummulative Distribution Plot", size=9)

        return var_pair, savefig(fig)
