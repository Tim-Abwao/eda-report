from eda_report.multivariate import MultiVariable
from io import BytesIO

import matplotlib
from matplotlib.figure import Figure
import seaborn as sns
from scipy.stats import probplot

import numpy as np

# Matplotlib configuration
matplotlib.rc("figure", dpi=150, autolayout=True)
matplotlib.rc("savefig", edgecolor="k", facecolor="w")
matplotlib.rc("font", family="serif")
matplotlib.rc("axes.spines", top=False, right=False)
matplotlib.use("agg")  # use non-interactive matplotlib back-end


def savefig(figure):
    """Saves the contents of a :class:`~matplotlib.figure.Figure` in PNG format,
    as bytes in a file-like object.

    This is a utility function helpful in by-passing the *filesystem*. Created
    graphs are stored in :class:`io.BytesIO` objects, and can then be read
    directly as *attributes*. This allows convenient, rapid in-memory access.

    :param figure: A *matplotlib Figure* with plotted axes.
    :type figure: :class:`matplotlib.figure.Figure`
    :return: A file-like object with the figure's contents.
    :rtype: :class:`io.BytesIO`
    """
    graph = BytesIO()
    figure.savefig(graph)

    return graph


class PlotUnivariate:
    def __init__(self, variable) -> None:
        self.variable = variable
        self.plot_graphs()

    def plot_graphs(self):
        """Plot graphs for the column/feature, based on variable type."""
        if self.variable.var_type == "numeric":
            self.variable._graphs = {
                "hist_and_boxplot": self._plot_histogram_and_boxplot(),
                "prob_plot": self._plot_prob_plot(),
                "run_plot": self._plot_run_plot(),
            }
            return self.variable
        elif self.variable.var_type in {"boolean", "categorical", "datetime"}:
            self.variable._graphs = {"bar_plot": self._plot_bar()}
            return self.variable

    def _plot_histogram_and_boxplot(self):
        """Get a boxplot and a histogram for a numeric column/feature."""
        # Create a figure and axes
        fig = Figure(figsize=(6, 6), linewidth=1)
        ax1, ax2 = fig.subplots(nrows=2, ncols=1)

        if self.variable.TARGET_DATA.nunique() in range(1, 11):
            palette = f"dark:{self.variable.graph_color}_r"
            sns.boxplot(
                y=self.variable.data,
                x=self.variable.TARGET_DATA,
                palette=palette,
                ax=ax1,
            )
            sns.histplot(
                x=self.variable.data,
                hue=self.variable.TARGET_DATA,
                palette=palette,
                kde=True,
                ax=ax2,
            )
            self._COLOR_CODED_GRAPHS.add("histogram & boxplot")
        else:
            ax1.boxplot(self.variable.data.dropna(), vert=False, notch=True)
            ax1.set_yticklabels([""])  # Remove y-tick labels
            ax1.set_xlabel(f"{self.variable.name}")

            sns.histplot(
                x=self.variable.data,
                kde=True,
                ax=ax2,
                color=self.variable.graph_color,
            )

        ax1.set_title(f"Box-plot of {self.variable.name}", size=12)
        ax2.set_title(f"Distribution plot of {self.variable.name}", size=12)

        return savefig(fig)

    def _plot_prob_plot(self):
        """Get a probability plot for a numeric column/feature."""
        # Create a figure and axes
        fig = Figure(figsize=(6, 4), linewidth=1)
        ax = fig.subplots()
        # Get quantile data.
        theoretical_quantiles, ordered_values = probplot(
            self.variable.data,
            fit=False,  # The OLS line of best fit will be plotted in regplot
        )
        # Plot the data and a line of best fit
        sns.regplot(
            x=theoretical_quantiles,
            y=ordered_values,
            ax=ax,
            color=self.variable.graph_color,
        )
        ax.set_title(f"Probability Plot of {self.variable.name}", size=12)
        ax.set_xlabel("Theoretical Quantiles (~ Standard Normal)")
        ax.set_ylabel("Ordered Values")

        return savefig(fig)

    def _plot_run_plot(self):
        """Get a run-sequence-plot/line-plot for a numeric column/feature."""
        # Create a figure and axes
        fig = Figure(figsize=(6, 4), linewidth=1)
        ax = fig.subplots()
        # Get a line plot of the data
        if self.variable.TARGET_DATA.nunique() in range(1, 11):
            sns.lineplot(
                x=self.variable.data.index,
                y=self.variable.data,
                hue=self.variable.TARGET_DATA,
                palette=f"dark:{self.variable.graph_color}_r",
                ax=ax,
            )
            self._COLOR_CODED_GRAPHS.add("run-plot")
        else:
            ax.plot(
                self.variable.data, marker=".", color=self.variable.graph_color
            )

        # Get boundaries of x-axis
        xmin = self.variable.data.index[0]
        xmax = self.variable.data.index[-1]
        # Plot a horizontal line at the 50th percentile
        p50 = self.variable.data.quantile(0.5)
        ax.hlines(p50, xmin, xmax, "grey", "--")
        ax.text(xmax, p50, " Median")
        # Plot a horizontal line at the 5th percentile
        p5 = self.variable.data.quantile(0.05)
        ax.hlines(p5, xmin, xmax, "grey", "--")
        ax.text(xmax, p5, " $5^{th}$ Percentile")
        # Plot a horizontal lines at the 95th percentile
        p95 = self.variable.data.quantile(0.95)
        ax.hlines(p95, xmin, xmax, "grey", "--")
        ax.text(xmax, p95, " $95^{th}$ Percentile")

        ax.tick_params(axis="x", rotation=45)  # rotate x-labels by 45°
        ax.set_title(f"Line Plot (Run Plot) of {self.variable.name}", size=12)
        ax.set_ylabel("Observed Value")
        ax.set_xlabel("Index")

        return savefig(fig)

    def _plot_bar(self):
        """Get a bar-plot for a categorical column/feature."""
        # Create a figure and axes
        fig = Figure(figsize=(6, 4), linewidth=1)
        ax = fig.subplots()

        if (
            self.variable.data.nunique() in range(1, 11)
            and self.variable.TARGET_DATA.nunique() in range(1, 11)
            and len(self.variable.data) == len(self.variable.TARGET_DATA)
            and set(self.variable.data) != set(self.variable.TARGET_DATA)
        ):
            sns.countplot(
                x=self.variable.data,
                hue=self.variable.TARGET_DATA,
                palette=f"dark:{self.variable.graph_color}_r",
                ax=ax,
            )
        else:
            # Include no more than 10 of the most common values
            top_10 = self.variable.data.value_counts().nlargest(10)
            sns.barplot(
                x=top_10.index.to_list(),
                y=top_10,
                palette=f"dark:{self.variable.graph_color}_r",
                ax=ax,
            )
            ax.tick_params(axis="x", rotation=45)
            ax.set_title(f"Bar-plot of {self.variable.name}", size=12)

        # Annotate bars
        for p in ax.patches:
            ax.annotate(
                f"{p.get_height():,}",
                ha="left",
                xy=(p.get_x(), p.get_height() * 1.02),
            )

        return savefig(fig)


class PlotMultiVariate:
    def __init__(self, multivariable) -> None:
        self.multivariable = multivariable

    def plot_graphs(self):
        if hasattr(self.multivariable, "var_pairs"):
            self._plot_joint_scatterplot()
            self._plot_joint_correlation()
            self.multivariable.bivariate_scatterplots = {}

            for var1, var2 in self.multivariable.var_pairs:
                self._regression_plot(var1, var2)
        return self.multivariable

    def _plot_joint_scatterplot(self):
        """Create a joint scatter-plot of all numeric columns."""
        if (
            self.multivariable.TARGET_VARIABLE is None
            or self.multivariable.data[
                self.multivariable.TARGET_VARIABLE
            ].nunique()
            > 10
        ):
            plot_params = {"data": self.multivariable.numeric_cols}
            subplot_params = {"color": self.multivariable.graph_color}

        else:  # Color-code plotted values by target variable
            if (
                self.multivariable.TARGET_VARIABLE
                in self.multivariable.numeric_cols
            ):
                numeric_cols_with_target = self.multivariable.numeric_cols
            else:  # Join the numeric data and target-variable data by index
                numeric_cols_with_target = (
                    self.multivariable.numeric_cols.merge(
                        self.multivariable.data[
                            self.multivariable.TARGET_VARIABLE
                        ],
                        left_index=True,
                        right_index=True,
                    )
                )
            plot_params = {
                "data": numeric_cols_with_target,
                "hue": self.multivariable.TARGET_VARIABLE,
                "palette": f"dark:{self.multivariable.graph_color}_r",
            }
            subplot_params = {}
            self._COLOR_CODED_GRAPHS.add("joint-scatterplot")

        fig = sns.PairGrid(**plot_params)
        fig.map_upper(  # Plot scatterplots in upper half
            sns.scatterplot, **subplot_params
        )
        fig.map_lower(  # Plot kdeplots in lower half
            sns.kdeplot, **subplot_params
        )
        fig.map_diag(  # Plot histograms in diagonal
            sns.histplot, kde=True, **subplot_params
        )
        fig.add_legend(bbox_to_anchor=(1.05, 1.05))

        self.joint_scatterplot = savefig(fig)

    def _plot_joint_correlation(self):
        """Plot a heatmap of the correlation among all numeric columns."""
        fig = Figure(figsize=(6, 6))
        ax = fig.subplots()
        sns.heatmap(
            self.multivariable.correlation_df,
            annot=True,
            yticklabels=True,
            mask=np.triu(self.multivariable.correlation_df),
            ax=ax,
            cmap=sns.light_palette(
                self.multivariable.graph_color, as_cmap=True
            ),
        )
        ax.tick_params(rotation=45)
        fig.suptitle("Correlation in Numeric Columns", size=15)

        self.multivariable.joint_correlation_heatmap = savefig(fig)

    def _regression_plot(self, var1, var2):
        """Create a scatterplot with a fitted linear regression line.

        :param var1: A numeric column/feature name
        :type var1: str
        :param var2: A numeric column/feature name
        :type var2: str
        """
        fig = Figure(figsize=(8.2, 4))
        ax1, ax2 = fig.subplots(nrows=1, ncols=2)
        # Scatter-plot with linear regression line
        sns.regplot(
            x=var1,
            y=var2,
            data=self.multivariable.data,
            ax=ax1,
            truncate=False,
            color=self.multivariable.graph_color,
        )
        # Empirical cummulative distribution function plots
        sns.ecdfplot(
            data=self.multivariable.data.loc[:, [var1, var2]],
            ax=ax2,
            palette=f"dark:{self.multivariable.graph_color}_r",
        )
        ax1.set_title(f"Scatter-plot - {var1} vs {var2}".title(), size=9)
        ax2.set_title("Empirical Cummulative Distribution Functions", size=9)

        self.multivariable.bivariate_scatterplots[(var1, var2)] = savefig(fig)


if __name__ == "__main__":
    data = sns.load_dataset("iris")
    print(PlotMultiVariate(MultiVariable(data)).plot_graphs())
