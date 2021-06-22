from textwrap import shorten

import seaborn as sns
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)
from PIL import Image
from scipy.stats import probplot

from eda_report.plotting import Fig, savefig
from eda_report.validate import validate_univariate_input


class Variable:
    """This is the blueprint for objects that analyse and plot one-dimensional
    datasets: a *single column/feature*.
    """

    def __init__(
        self, data, *, graph_color="orangered", name=None, target_data=None
    ):
        """Initialise an instance of :class:`Variable`.

        :param data: The data to process.
        :type data: array-like, sequence, iterable.
        :param graph_color: The color to apply to the graphs created,
            defaults to 'orangered'.
        :type graph_color: str, optional
        :param name: The feature's name.
        :type name: str, optional
        :param target_data: Data for the target variable (dependent
            feature). Currently used to group and color-code values in graphs.
        :type target_data: array-like, optional
        """
        self.data = validate_univariate_input(data)
        #: The *name* of the *column/feature*. If unspecified in the ``name``
        #: argument during instantiation, this will be taken as the value of
        #: the ``name`` attribute of the input data.
        self.name = self._get_name(name)
        #: The *type* of feature; either *boolean*, *categorical*, *datetime*
        #:  or *numeric*.
        self.var_type = self._get_variable_type()
        #: *Summary statistics* for the *column/feature*, as a
        #: :class:`pandas.DataFrame`.
        self.statistics = self._get_summary_statistics()
        #: The *number of unique values* present in the *column/feature*.
        self.num_unique = self.data.nunique()
        #: The set of *unique values* present in the *column/feature*.
        self.unique = set(self.data.unique())
        #: The number of *missing values*.
        self.missing = self._get_missing_values()
        #: The *color* applied to the created graphs.
        self.graph_color = graph_color
        self.TARGET_DATA = validate_univariate_input(target_data)
        self._COLOR_CODED_GRAPHS = set()
        # Get graphs for the column/feature as a dict of file-like objects.
        self._graphs = self._plot_graphs()

    def __repr__(self):
        """Creates the string representation for :class:`Variable` objects."""
        return f"""\
            Overview
            ========
Name: {self.name},
Type: {self.var_type},
Unique Values: {shorten(f'{self.num_unique} -> {self.unique}', 60)},
Missing Values: {self.missing}

        Summary Statistics
        ==================
{self.statistics}
"""

    def show_graphs(self):  # pragma: no cover
        """Display the plotted graphs for the *column/feature*."""
        for graph in self._graphs.values():
            image = Image.open(graph)
            image.show()

    def _get_name(self, name=None):
        """Set the feature's name.

        :param name: The name to give the feature, defaults to None
        :type name: str, optional
        """
        if name:
            self.data = self.data.rename(name)

        return self.data.name

    def _get_variable_type(self):
        """Get the variable type: 'categorical' or 'numeric'."""
        if is_numeric_dtype(self.data):
            if is_bool_dtype(self.data) or set(self.data.dropna()) == {0, 1}:
                return "boolean"
            else:
                # Only int and float types
                return "numeric"
        elif is_datetime64_any_dtype(self.data):
            self.data = self.data.dt.strftime("%c")
            return "datetime"
        else:
            # Handle str, etc as categorical
            return "categorical"

    def _get_summary_statistics(self):
        """Get summary statistics for the column/feature."""
        if self.var_type == "numeric":
            return self._numeric_summary_statictics()
        elif self.var_type in {"boolean", "categorical", "datetime"}:
            self.data = self.data.astype("category")
            return self._categorical_summary_statistics()

    def _numeric_summary_statictics(self):
        """Get summary statistics for a numeric column/feature."""
        summary = self.data.describe()
        summary.index = [
            "Number of observations",
            "Average",
            "Standard Deviation",
            "Minimum",
            "Lower Quartile",
            "Median",
            "Upper Quartile",
            "Maximum",
        ]
        summary["Skewness"] = self.data.skew()
        summary["Kurtosis"] = self.data.kurt()

        return summary.round(7).to_frame()

    def _categorical_summary_statistics(self):
        """Get summary statistics for a categorical column/feature."""
        summary = self.data.describe()[["count", "unique", "top"]]
        summary.index = [
            "Number of observations",
            "Unique values",
            "Mode (Highest occurring value)",
        ]

        # Get most common items and their relative frequency (%)
        most_common_items = self.data.value_counts().head()
        n = len(self.data)
        self.most_common_items = most_common_items.apply(
            lambda x: f"{x} ({x / n:.2%})"
        ).to_frame()

        return summary.to_frame()

    def _get_missing_values(self):
        """Get the number of missing values in the column/feature."""
        missing_values = self.data.isna().sum()
        if missing_values == 0:
            return "None"
        else:
            return f"{missing_values} ({missing_values / len(self.data):.2%})"

    def _plot_graphs(self):
        """Plot graphs for the column/feature, based on variable type."""
        if self.var_type == "numeric":
            return {
                "hist_and_boxplot": self._plot_histogram_and_boxplot(),
                "prob_plot": self._plot_prob_plot(),
                "run_plot": self._plot_run_plot(),
            }
        elif self.var_type in {"boolean", "categorical", "datetime"}:
            return {"bar_plot": self._plot_bar()}

    def _plot_histogram_and_boxplot(self):
        """Get a boxplot and a histogram for a numeric column/feature."""
        # Create a figure and axes
        fig = Fig(figsize=(6, 6), linewidth=1)
        ax1, ax2 = fig.subplots(nrows=2, ncols=1)

        if self.TARGET_DATA.nunique() in range(1, 11):
            palette = f"dark:{self.graph_color}_r"
            sns.boxplot(
                y=self.data, x=self.TARGET_DATA, palette=palette, ax=ax1
            )
            sns.histplot(
                x=self.data,
                hue=self.TARGET_DATA,
                palette=palette,
                kde=True,
                ax=ax2,
            )
            self._COLOR_CODED_GRAPHS.add("histogram & boxplot")
        else:
            ax1.boxplot(self.data.dropna(), vert=False, notch=True)
            ax1.set_yticklabels([""])  # Remove y-tick labels
            ax1.set_xlabel(f"{self.name}")

            sns.histplot(x=self.data, kde=True, ax=ax2, color=self.graph_color)

        ax1.set_title(f"Box-plot of {self.name}", size=12)
        ax2.set_title(f"Distribution plot of {self.name}", size=12)

        return savefig(fig)

    def _plot_prob_plot(self):
        """Get a probability plot for a numeric column/feature."""
        # Create a figure and axes
        fig = Fig(figsize=(6, 4), linewidth=1)
        ax = fig.subplots()
        # Get quantile data.
        theoretical_quantiles, ordered_values = probplot(
            self.data,
            fit=False,  # The OLS line of best fit will be plotted in regplot
        )
        # Plot the data and a line of best fit
        sns.regplot(
            x=theoretical_quantiles,
            y=ordered_values,
            ax=ax,
            color=self.graph_color,
        )
        ax.set_title(f"Probability Plot of {self.name}", size=12)
        ax.set_xlabel("Theoretical Quantiles (~ Standard Normal)")
        ax.set_ylabel("Ordered Values")

        return savefig(fig)

    def _plot_run_plot(self):
        """Get a run-sequence-plot/line-plot for a numeric column/feature."""
        # Create a figure and axes
        fig = Fig(figsize=(6, 4), linewidth=1)
        ax = fig.subplots()
        # Get a line plot of the data
        if self.TARGET_DATA.nunique() in range(1, 11):
            sns.lineplot(
                x=self.data.index,
                y=self.data,
                hue=self.TARGET_DATA,
                palette=f"dark:{self.graph_color}_r",
                ax=ax,
            )
            self._COLOR_CODED_GRAPHS.add("run-plot")
        else:
            ax.plot(self.data, marker=".", color=self.graph_color)

        # Get boundaries of x-axis
        xmin = self.data.index[0]
        xmax = self.data.index[-1]
        # Plot a horizontal line at the 50th percentile
        p50 = self.data.quantile(0.5)
        ax.hlines(p50, xmin, xmax, "grey", "--")
        ax.text(xmax, p50, " Median")
        # Plot a horizontal line at the 5th percentile
        p5 = self.data.quantile(0.05)
        ax.hlines(p5, xmin, xmax, "grey", "--")
        ax.text(xmax, p5, " $5^{th}$ Percentile")
        # Plot a horizontal lines at the 95th percentile
        p95 = self.data.quantile(0.95)
        ax.hlines(p95, xmin, xmax, "grey", "--")
        ax.text(xmax, p95, " $95^{th}$ Percentile")

        ax.tick_params(axis="x", rotation=45)  # rotate x-labels by 45°
        ax.set_title(f"Line Plot (Run Plot) of {self.name}", size=12)
        ax.set_ylabel("Observed Value")
        ax.set_xlabel("Index")

        return savefig(fig)

    def _plot_bar(self):
        """Get a bar-plot for a categorical column/feature."""
        # Create a figure and axes
        fig = Fig(figsize=(6, 4), linewidth=1)
        ax = fig.subplots()

        if (
            self.data.nunique() in range(1, 11)
            and self.TARGET_DATA.nunique() in range(1, 11)
            and len(self.data) == len(self.TARGET_DATA)
            and set(self.data) != set(self.TARGET_DATA)
        ):
            sns.countplot(
                x=self.data,
                hue=self.TARGET_DATA,
                palette=f"dark:{self.graph_color}_r",
                ax=ax,
            )
            self._COLOR_CODED_GRAPHS.add("bar-plot")
        else:
            # Include no more than 10 of the most common values
            top_10 = self.data.value_counts().nlargest(10)
            sns.barplot(
                x=top_10.index.to_list(),
                y=top_10,
                palette=f"dark:{self.graph_color}_r",
                ax=ax,
            )
            ax.tick_params(axis="x", rotation=45)
            ax.set_title(f"Bar-plot of {self.name}", size=12)

        # Annotate bars
        for p in ax.patches:
            ax.annotate(
                f"{p.get_height():,}",
                ha="left",
                xy=(p.get_x(), p.get_height() * 1.02),
            )

        return savefig(fig)
