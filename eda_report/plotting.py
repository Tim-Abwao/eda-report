from collections.abc import Iterable
from io import BytesIO
from typing import Optional

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
matplotlib.rc("figure", autolayout=True, dpi=250, figsize=(6.5, 4))
matplotlib.rc("font", family="serif")
matplotlib.rc("axes.spines", top=False, right=False)
matplotlib.rc("axes", titlesize=12, titleweight=500)
matplotlib.use("agg")  # use non-interactive matplotlib back-end


def savefig(figure: Figure) -> BytesIO:
    """Saves the contents of a :class:`~matplotlib.figure.Figure` in PNG
    format, as bytes in a file-like object.

    This is a utility function helpful in by-passing the *filesystem*. Graphs
    are stored in :class:`~io.BytesIO` objects, and can then be read
    directly as *attributes*, thus allowing rapid in-memory access.

    Args:
        figure (Figure): A matplotlib figure with graph content.

    Returns:
        BytesIO: A graph in PNG format as bytes.
    """
    graph = BytesIO()
    figure.savefig(graph, format="png")

    return graph


class BasePlot:
    """Defines general plot settings, such as the the color palette and hue.

    Args:
        graph_color (str, optional): The color to apply to the generated
            graphs. Defaults to "cyan".
        hue (Optional[Iterable], optional): Data to use to group values.
            Defaults to None.
    """

    def __init__(
        self, *, graph_color: str = "cyan", hue: Optional[Iterable] = None
    ) -> None:
        self.GRAPH_COLOR = graph_color
        self.HUE = validate_univariate_input(hue)
        sns.set_palette(
            f"dark:{self.GRAPH_COLOR}_r",
            n_colors=2 if self.HUE is None else self.HUE.nunique(),
        )

        #: bool: A flag that determines whether or not to use the supplied
        #: ``hue`` to group values. True if ``hue`` has manageable cardinality.
        self.COLOR_GROUPS = (  # True if below condition holds
            self.HUE is not None and self.HUE.nunique() in range(2, 11)
        )
        self._COLOR_GROUPED_GRAPHS = set()


class PlotVariable(BasePlot):
    """Plots instances of :class:`~eda_report.univariate.Variable`:

    - *Box-plots*, *dist-plots* and *normal-probability-plots* for
      numeric variables.
    - *Bar-plots* for categorical variables.

    Args:
        variable (Variable): The data to plot.
        graph_color (str, optional): The color to apply to the generated
            graphs. Defaults to "cyan".
        hue (Optional[Series], optional): Data to use to group values.
            Defaults to None.

    Attributes
        graphs (Dict[str, BytesIO]): A dictionary of graphs, with graph names
           as keys and file-objects containing plotted graphs as values.
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

        For **numeric** variables, a *box-plot*, *dist-plot* and *probability
        plot* are produced.

        For **categorical**, **boolean** or **datetime** objects, only a *bar
        plot* is produced.
        """
        if self.variable.var_type == "numeric":
            self.graphs = {
                "box_plot": self._plot_box(),
                "kde_plot": self._plot_dist(),
                "prob_plot": self._plot_prob(),
            }
        else:  # {"boolean", "categorical", "datetime"}:
            self.graphs = {"bar_plot": self._plot_bar()}

    def _plot_box(self) -> BytesIO:
        """Get a boxplot for a numeric variable.

        Returns:
            BytesIO: The boxplot in PNG format.
        """
        fig = Figure()
        ax = fig.subplots()
        sns.boxplot(
            x=self.variable.data,
            y=self.HUE,
            ax=ax,
            fliersize=4,
            notch=True,
            orient="h",
            saturation=0.85,
            width=0.2,
        )
        ax.set_title(f"Box-plot of {self.variable.name}")

        if self.HUE is not None:
            self._COLOR_GROUPED_GRAPHS.add("box_plot")

        return savefig(fig)

    def _plot_dist(self) -> BytesIO:
        """Get a dist-plot for a numeric variable.

        Returns:
            BytesIO: The dist-plot in PNG format.
        """
        fig = Figure()
        ax = fig.subplots()
        sns.kdeplot(x=self.variable.data, ax=ax, fill=True, hue=self.HUE)
        ax.set_title(f"Distribution plot of {self.variable.name}")

        if self.HUE is not None:
            self._COLOR_GROUPED_GRAPHS.add("kde_plot")

        return savefig(fig)

    def _plot_prob(self) -> BytesIO:
        """Get a probability plot for a numeric variable.

        Returns:
            BytesIO: The probability plot in PNG.
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

    def _plot_bar(self) -> BytesIO:
        """Get a barplot for a categorical, boolean or datetime variable.

        Returns:
            BytesIO: The barplot in PNG format.
        """
        fig = Figure()
        ax = fig.subplots()

        # Include no more than 10 of the most common values
        top_10 = self.variable.data.value_counts().nlargest(10)
        sns.barplot(
            x=list(top_10.index),
            y=top_10,
            ax=ax,
            palette=f"dark:{self.GRAPH_COLOR}_r",
        )
        ax.tick_params(axis="x", rotation=90)

        if (num_unique := self.variable.num_unique) > 10:
            ax.set_title(
                f"Bar-plot of {self.variable.name} (Top 10 of {num_unique})"
            )
        else:
            ax.set_title(f"Bar-plot of {self.variable.name}")

        # Annotate bars
        for p in ax.patches:
            ax.annotate(
                f"{p.get_height():,.0f}",
                ha="center",
                size=8,
                xy=(p.get_x() + p.get_width() / 2, p.get_height() * 1.02),
            )

        return savefig(fig)


class PlotMultiVariable(BasePlot):
    """Plots instances of :class:`~eda_report.multivariate.MultiVariable`.

    Produces a *correlation heatmap*, *scatter-plots* and *ecdf-plots*, if
    2 or more numeric columns are present, with more than 5% of their values
    unique.

    Args:
        variables (MultiVariable): The data to plot.
        graph_color (str, optional): The color to apply to the generated
            graphs. Defaults to "cyan".
        hue (Optional[Series], optional): Data to use to group values.
            Defaults to None.

    Attributes
    ----------
        graphs (Dict[str, Union[BytesIO, dict[tuple(str, str), BytesIO]]]):
            A dictionary of graphs, with graph names as keys, and file-objects
            containing the plotted graphs as values.

            Bi-variate scatterplots are further nested in a dict of
            :class:`~io.BytesIO` objects, with tuples (col_i, col_j) as keys.
    """

    def __init__(
        self,
        variables: MultiVariable,
        *,
        graph_color: str = "cyan",
        hue: Optional[Series] = None,
    ) -> None:
        super().__init__(graph_color=graph_color, hue=hue)
        self.variables = variables
        self._plot_graphs()

    def _plot_graphs(self) -> None:
        """Get a heatmap of the correlation in all numeric columns, and
        scatter-plots & ecdf-plots of numeric column pairs.
        """
        if hasattr(self.variables, "var_pairs"):
            self.bivariate_scatterplots = {
                (var_pair): self._regression_plot(*var_pair)
                for var_pair in tqdm(
                    self.variables.var_pairs,
                    bar_format="{desc}: {percentage:3.0f}%|{bar:35}| "
                    + "{n_fmt}/{total_fmt} numeric pairs.",
                    desc="Bivariate analysis",
                    dynamic_ncols=True,
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

        Returns:
            BytesIO: The heatmap in PNG format as bytes in a file-like object.
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

    def _regression_plot(self, var1: str, var2: str) -> BytesIO:
        """Get a scatter-plot and ecdf-plot for the provided numeric columns.

        Args:
            var1, var2 (str): A numeric column label.

        Returns:
            BytesIO: The scatter-plot and ecdf-plot (subplots) in PNG format.
        """
        fig = Figure(figsize=(8.2, 4))
        ax1, ax2 = fig.subplots(nrows=1, ncols=2)

        sns.regplot(x=var1, y=var2, data=self.variables.data, ax=ax1)

        pair_data = self.variables.data.loc[:, [var1, var2]]
        normalized_data = (pair_data - pair_data.mean()) / pair_data.std()
        sns.ecdfplot(
            data=normalized_data, ax=ax2, palette=f"dark:{self.GRAPH_COLOR}_r"
        )
        ax1.set_title(f"Scatter-plot - {var1} vs {var2}".title(), size=9)
        ax2.set_title("Empirical Cummulative Distribution Plot", size=9)

        return savefig(fig)
