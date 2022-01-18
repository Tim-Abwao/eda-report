from io import BytesIO
from typing import Optional
from collections.abc import Iterable

import matplotlib
import numpy as np
import seaborn as sns
from matplotlib.figure import Figure
from pandas import Series
from scipy.stats import probplot
from tqdm import tqdm

from eda_report.multivariate import MultiVariable
from eda_report.univariate import Variable
from eda_report.validate import validate_univariate_input

# Matplotlib configuration
matplotlib.rc("figure", autolayout=True, dpi=250, figsize=(6.4, 4))
matplotlib.rc("font", family="serif")
matplotlib.rc("axes.spines", top=False, right=False)
matplotlib.rc("axes", titlesize=12, titleweight=500)
matplotlib.use("agg")  # use non-interactive matplotlib back-end


def savefig(figure: Figure) -> BytesIO:
    """Saves the contents of a :class:`~matplotlib.figure.Figure` in PNG format,
    as bytes in a file-like object.

    This is a utility function helpful in by-passing the *filesystem*. Graphs
    are stored in :class:`~io.BytesIO` objects, and can then be read
    directly as *attributes*, thus allowing rapid in-memory access.

    Parameters
    ----------
    figure : Figure
        A matplotlib figure with graph content.

    Returns
    -------
    BytesIO
        A graph in PNG format as bytes.
    """
    graph = BytesIO()
    figure.savefig(graph, format="png")

    return graph


class BasePlot:
    """The base class for plotting objects.

    This is where general plot settings such as the the color palette and hue
    are set.

    Parameters
    ----------
    graph_color : str, optional
        The color to apply to the generated graphs, by default "cyan".
    hue : Optional[Iterable]
        Data to use to group values & color-code graphs, by default None.
    """

    def __init__(
        self, *, graph_color: str = "cyan", hue: Optional[Iterable] = None
    ) -> None:
        self.GRAPH_COLOR = graph_color
        self.HUE = None if hue is None else validate_univariate_input(hue)
        sns.set_palette(
            f"dark:{self.GRAPH_COLOR}_r",
            n_colors=2 if self.HUE is None else self.HUE.nunique(),
        )

        #: bool: A flag that determines whether or not to use the supplied
        #: ``hue``. True if ``hue`` has manageable cardinality, False
        #: otherwise.
        self.COLOR_CODE_GRAPHS = (  # True if below condition holds
            self.HUE is not None and self.HUE.nunique() in range(2, 11)
        )
        self._COLOR_CODED_GRAPHS = set()


class PlotVariable(BasePlot):
    """This defines objects that plot instances of
    :class:`~eda_report.univariate.Variable`, which have one-dimensional data.

    Parameters
    ----------
    variable : Variable
        The data to plot.
    graph_color : str, optional
        The color to apply to the generated graphs, by default "cyan".
    hue : Optional[Iterable]
        Data to use to group values & color-code graphs, by default None.

    Attributes
    ----------
    graphs : Dict[str, BytesIO]
        A dictionary of graphs, with graph names as keys and file-objects
        containing plotted graphs as values.
    """

    def __init__(
        self,
        variable: Variable,
        *,
        graph_color: str = "cyan",
        hue: Optional[Series] = None,
    ) -> None:
        super().__init__(graph_color=graph_color, hue=hue)
        self.variable = variable
        self._plot_graphs()

    def _plot_graphs(self) -> None:
        """Plot graphs based on the ``Variable`` type.

        For **numeric** variables, a *box-plot*, *histogram*, *probability
        plot* and *run plot* are produced.

        For **categorical**, **boolean** or **datetime** objects, only a *bar
        plot* is produced.
        """
        if self.variable.var_type == "numeric":
            self.graphs = {
                "boxplot": self._plot_boxplot(),
                "histogram": self._plot_distplot(),
                "prob_plot": self._plot_prob_plot(),
                "run_plot": self._plot_run_plot(),
            }
        else:  # {"boolean", "categorical", "datetime"}:
            self.graphs = {"bar_plot": self._plot_bar()}

    def _plot_boxplot(self) -> BytesIO:
        """Get a boxplot for a numeric variable.

        Returns
        -------
        BytesIO
            The boxplot in PNG format as bytes in a file-object.
        """
        fig = Figure()
        ax = fig.subplots()

        if self.COLOR_CODE_GRAPHS:
            sns.boxplot(y=self.variable.data, x=self.HUE, ax=ax)
            self._COLOR_CODED_GRAPHS.add("boxplot")
        else:
            ax.boxplot(self.variable.data.dropna(), vert=False, notch=True)
            ax.set_yticklabels([""])  # Remove y-tick label
            ax.set_xlabel(f"{self.variable.name}")

        ax.set_title(f"Box-plot of {self.variable.name}")
        return savefig(fig)

    def _plot_distplot(self) -> BytesIO:
        """Get a distplot for a numeric variable.

        Returns
        -------
        BytesIO
            The distplot in PNG format as bytes in a file-object.
        """
        fig = Figure()
        ax = fig.subplots()

        if self.COLOR_CODE_GRAPHS:
            hue = self.HUE
            self._COLOR_CODED_GRAPHS.add("histogram")
        else:
            hue = None

        sns.histplot(
            x=self.variable.data,
            hue=hue,
            kde=True,
            ax=ax,
            palette=f"dark:{self.GRAPH_COLOR}_r",
        )

        ax.set_title(f"Distribution plot of {self.variable.name}")
        return savefig(fig)

    def _plot_prob_plot(self) -> BytesIO:
        """Get a probability plot for a numeric variable.

        Returns
        -------
        BytesIO
            The probability plot in PNG format as bytes in a file-object.
        """
        fig = Figure()
        ax = fig.subplots()

        theoretical_quantiles, ordered_values = probplot(
            self.variable.data,
            fit=False,  # The line of best fit will be plotted in regplot
        )
        sns.regplot(x=theoretical_quantiles, y=ordered_values, ax=ax)

        ax.set_title(f"Probability Plot of {self.variable.name}")
        ax.set_xlabel("Theoretical Quantiles (~ Standard Normal)")
        ax.set_ylabel("Ordered Values")
        return savefig(fig)

    def _plot_run_plot(self) -> BytesIO:
        """Get a run plot for a numeric variable.

        Returns
        -------
        BytesIO
            The run plot in PNG format as bytes in a file-object.
        """
        fig = Figure()
        ax = fig.subplots()

        if self.COLOR_CODE_GRAPHS:
            sns.lineplot(
                x=self.variable.data.index,
                y=self.variable.data,
                hue=self.HUE,
                ax=ax,
                palette=f"dark:{self.GRAPH_COLOR}_r",
            )
            self._COLOR_CODED_GRAPHS.add("run-plot")
        else:
            ax.plot(self.variable.data, marker=".", color=self.GRAPH_COLOR)

        ax.tick_params(axis="x", rotation=45)
        ax.set_title(f"Run Plot of {self.variable.name}")
        ax.set_ylabel("Observed Value")
        ax.set_xlabel("Index")

        # Get x-axis boundaries
        xmin, xmax = self.variable.data.index[[0, -1]]

        # Get percentiles and plot them as horizontal lines
        p5 = self.variable.data.quantile(0.05)
        p50 = self.variable.data.quantile(0.5)
        p95 = self.variable.data.quantile(0.95)

        ax.hlines(p5, xmin, xmax, "grey", "--")
        ax.text(xmax, p5, " $5^{th}$ Percentile")

        ax.hlines(p50, xmin, xmax, "grey", "--")
        ax.text(xmax, p50, " Median")

        ax.hlines(p95, xmin, xmax, "grey", "--")
        ax.text(xmax, p95, " $95^{th}$ Percentile")

        return savefig(fig)

    def _plot_bar(self) -> BytesIO:
        """Get a barplot for a categorical, boolean or datetime variable.

        Returns
        -------
        BytesIO
            The barplot in PNG format as bytes in a file-object.
        """
        fig = Figure(figsize=(6, 4), linewidth=1)
        ax = fig.subplots()

        # Include no more than 10 of the most common values
        top_10 = self.variable.data.value_counts().nlargest(10)

        if self.COLOR_CODE_GRAPHS:
            data_with_hue = (
                self.variable.data.to_frame(name="data")
                .assign(_hue_=self.HUE.values)
                .query("data in @top_10.index")
            )
            sns.countplot(data=data_with_hue, x="data", hue="_hue_", ax=ax)
            self._COLOR_CODED_GRAPHS.add("bar_plot")
        else:
            ax.bar(top_10.index.to_list(), top_10)

        ax.tick_params(axis="x", rotation=90)

        if self.variable.num_unique > 10:
            ax.set_title(
                f"Bar-plot of {self.variable.name} (Top 10 of "
                f"{self.variable.num_unique})"
            )
        else:
            ax.set_title(f"Bar-plot of {self.variable.name}")

        # Annotate bars
        for p in ax.patches:
            ax.annotate(
                f"{p.get_height():,}",
                ha="left",
                xy=(p.get_x(), p.get_height() * 1.02),
                size=7,
            )

        return savefig(fig)


class PlotMultiVariable(BasePlot):
    """This defines objects that plot instances of
    :class:`~eda_report.multivariate.MultiVariable`, which have
    two-dimensional data.

    Parameters
    ----------
    variable : MultiVariable
        The data to plot.
    graph_color : str, optional
        The color to apply to the generated graphs, by default "cyan".
    hue : Optional[Iterable]
        Data to use to group values & color-code graphs, by default None.

    Attributes
    ----------
    graphs : Dict[str, Union[BytesIO, dict[tuple(str, str), BytesIO]]]
        A dictionary of graphs, with graph names as keys, and file-objects
        containing the plotted graphs as values.

        Bi-variate scatterplots are further nested in a dict of
        :class:`~io.BytesIO` objects, with tuples (col_i, col_j) as keys.
    """

    def __init__(
        self,
        multivariable: MultiVariable,
        *,
        graph_color: str = "cyan",
        hue: Optional[Series] = None,
    ) -> None:
        super().__init__(graph_color=graph_color, hue=hue)
        self.multivariable = multivariable
        self._plot_graphs()

    def _plot_graphs(self) -> None:
        """Get a heatmap of the correlation in all numeric columns, and
        scatter-plots & ecdf-plots of numeric column pairs.
        """
        if hasattr(self.multivariable, "var_pairs"):
            self.bivariate_scatterplots = {
                (var_pair): self._regression_plot(*var_pair)
                for var_pair in tqdm(
                    self.multivariable.var_pairs,
                    bar_format="{desc}: {percentage:3.0f}%|{bar:35}| "
                    + "{n_fmt}/{total_fmt} numeric pairs.",
                    dynamic_ncols=True,
                    desc="Bivariate analysis",
                )
            }
            self.graphs = {
                "correlation_heatmap": self._plot_correlation_heatmap(),
                "scatterplots": self.bivariate_scatterplots,
            }
        else:
            self.graphs = None

    def _plot_correlation_heatmap(self) -> BytesIO:
        """Get a heatmap of the correlation among all numeric columns.

        Returns
        -------
        BytesIO
            The heatmap in PNG format as bytes in a file-like object.
        """
        fig = Figure(figsize=(6, 6))
        ax = fig.subplots()

        sns.heatmap(
            self.multivariable.correlation_df,
            annot=True,
            center=0,
            yticklabels=True,
            mask=np.triu(self.multivariable.correlation_df),
            ax=ax,
            cmap=sns.light_palette(self.GRAPH_COLOR, as_cmap=True),
        )
        ax.tick_params(rotation=45)
        fig.suptitle("Correlation in Numeric Columns", size=15)

        return savefig(fig)

    def _regression_plot(self, var1: str, var2: str) -> BytesIO:
        """Get a scatter-plot and ecdf-plot for the provided numeric columns.

        Parameters
        ----------
        var1, var2 : str
            A numeric column label.

        Returns
        -------
        BytesIO
            The scatter-plot and ecdf-plot (subplots) in PNG format as bytes
            in a file-like object.
        """
        fig = Figure(figsize=(8.2, 4))
        ax1, ax2 = fig.subplots(nrows=1, ncols=2)

        sns.regplot(x=var1, y=var2, data=self.multivariable.data, ax=ax1)

        sns.ecdfplot(
            data=self.multivariable.data.loc[:, [var1, var2]],
            ax=ax2,
            palette=f"dark:{self.GRAPH_COLOR}_r",
        )
        ax1.set_title(f"Scatter-plot - {var1} vs {var2}".title(), size=9)
        ax2.set_title("Empirical Cummulative Distribution Plot", size=9)

        return savefig(fig)
