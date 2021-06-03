from itertools import combinations
import logging
import numpy as np
import seaborn as sns
from PIL import Image
from tqdm import tqdm

from eda_report.plotting import Fig, savefig
from eda_report.validate import (
    validate_multivariate_input,
    validate_target_variable,
)


class MultiVariable:
    """The blueprint for containers to hold the properties of data with
    *multiple columns/features*.

    The input data is expected to be a ``pandas.DataFrame``. If the data is of
    any other type, then there'll be an attempt to explicitly convert it to a
    ``DataFrame``. If this fails, an :class:`~eda_report.exceptions.InputError`
    is raised.
    """

    def __init__(self, data, *, graph_color="orangered", target_variable=None):
        """Initialise an instance of
        :class:`~eda_report.multivariate.MultiVariable`.

        :param data: The data to process, ideally a ``pandas.DataFrame``
            with several columns.
        :type data: array-like, sequence, iterable, dict
        :param graph_color: The color to apply to the graphs created,
            defaults to 'orangered'. See the *matplotlib* `list of named
            colors`_ for all available options.
        :type graph_color: str, optional
        :param target_variable: The target variable (dependent feature). An
            *integer value* is treated as a *column index*, whereas a *string*
            is treated as a *column label*.
        :type target_variable: int, str, optional

        .. _`list of named colors`:
            https://matplotlib.org/stable/gallery/color/named_colors.html
        """
        self.data = validate_multivariate_input(data)
        #: The color applied to the created graphs.
        self.graph_color = graph_color
        self.TARGET_VARIABLE = validate_target_variable(
            data=self.data, target_variable=target_variable
        )
        #: A ``DataFrame`` with all the *numeric columns/features* present.
        self.numeric_cols = self._select_cols("number")
        #: A ``DataFrame`` with all the *categorical columns/features*
        #: present. Please note that **boolean features** are also
        #: **considered categorical** in this context.
        self.categorical_cols = self._select_cols("object", "bool")
        #: A ``DataFrame`` of Pearson correlation coefficients for the
        #: *numeric columns/features*.
        self.correlation_df = self._get_correlation()
        #: Get brief descriptions of the nature of correlation between
        #: numerical feature pairs.
        self.corr_type = {}
        self.bivariate_scatterplots = {}
        self._get_bivariate_analysis()

    def __repr__(self):
        """Create string representation for :class:`Multivariable` objects."""
        # Get a list of numeric features
        if self.numeric_cols is None:
            numeric_cols = ""
        else:
            numeric_cols = self.numeric_cols.columns.to_list()

        # Get a list of categorical features
        if self.categorical_cols is None:
            categorical_cols = ""
        else:
            categorical_cols = self.categorical_cols.columns.to_list()

        return f"""\
        Overview
        ========
Numeric features: {', '.join(numeric_cols)}
Categorical features: {', '.join(categorical_cols)}

        Summary Statistics (Numeric features)
        =====================================
{self.numeric_cols.describe() if numeric_cols != '' else 'N/A'}

        Summary Statistics (Categorical features)
        =========================================
{self.categorical_cols.describe() if categorical_cols != '' else 'N/A'}

        Bivariate Analysis (Correlation)
        ================================
{self._corr_description if hasattr(self, '_corr_description') else 'N/A'}
"""

    def show_correlation_heatmap(self):
        """Display a heatmap of Pearson correlation coefficients for all
        *numeric columns/features* present.
        """
        if hasattr(self, "joint_correlation_heatmap"):
            image = Image.open(self.joint_correlation_heatmap)
            image.show()
        else:
            logging.info("Not enough numeric variables to compare.")

    def show_joint_scatterplot(self):
        """Display a joint scatter-plot of all the *numeric columns/features*
        present.
        """
        if hasattr(self, "joint_scatterplot"):
            image = Image.open(self.joint_scatterplot)
            image.show()
        else:
            logging.info("Not enough numeric variables to compare.")

    def _select_cols(self, *dtypes):
        """Get a DataFrame including only the data types specified.

        :param dtypes: The column data type(s) to include.
        :type dtypes: str
        :return: A ``DataFrame`` with columns of the specified data type(s), or
            ``None`` if no column is of that data type.
        :rtype: A ``DataFrame``, or ``None``
        """
        selected_cols = self.data.select_dtypes(include=dtypes)
        return selected_cols if selected_cols.shape[1] > 0 else None

    def _get_correlation(self):
        """Get a DataFrame of the correlation coefficients for numeric
        columns.
        """
        return None if self.numeric_cols is None else self.data.corr()

    def _get_bivariate_analysis(self):
        """Compare numeric variable pairs."""
        if self.numeric_cols is not None and self.numeric_cols.shape[1] > 1:
            self._plot_joint_scatterplot()
            self._plot_joint_correlation()
            self._compare_variable_pairs()
            self._corr_description = "\n".join(
                [
                    f"{var_pair[0]} & {var_pair[1]} --> {corr_description}"
                    for var_pair, corr_description in self.corr_type.items()
                ]
            )
        else:
            logging.warning(
                "Skipped Bivariate Analysis: "
                "Not enough numeric variables to compare."
            )

    def _create_palette(self, n_colors=10):
        """Get a color palette based on the set graph color."""
        return sns.light_palette(self.graph_color, n_colors=n_colors + 1,)[
            1:  # Discard the first, which is too light
        ]

    def _plot_joint_scatterplot(self):
        """Create a joint scatter-plot of all numeric columns."""
        if self.TARGET_VARIABLE is not None:
            target_data = self.data[self.TARGET_VARIABLE]

            if target_data.nunique() > 10:
                # Too many levels in target variable would clutter the graph
                logging.warning(
                    f"Target variable '{target_data.name}' not used to group "
                    "values in joint scatterplot. It has too many levels "
                    f"({target_data.nunique()}), and would clutter the graph."
                )
                # Treat target variable as if None
                plot_params = {"data": self.numeric_cols}
                subplot_params = {"color": self.graph_color}

            elif target_data.nunique() in range(1, 11):
                # Color-code plotted values by target variable
                if self.TARGET_VARIABLE in self.numeric_cols:
                    numeric_cols_with_target = self.numeric_cols
                else:  # Combine the numeric data and target data
                    numeric_cols_with_target = self.numeric_cols.merge(
                        target_data,
                        left_index=True,
                        right_index=True,
                    )
                plot_params = {
                    "data": numeric_cols_with_target,
                    "hue": self.TARGET_VARIABLE,
                    "palette": self._create_palette(
                        n_colors=self.data[self.TARGET_VARIABLE].nunique()
                    ),
                }
                subplot_params = {}

        else:  # When self.TARGET_VARIABLE is None
            plot_params = {"data": self.numeric_cols}
            subplot_params = {"color": self.graph_color}

        fig = sns.PairGrid(**plot_params)
        fig.map_upper(  # Plot scatterplots in upper half
            sns.scatterplot, **subplot_params
        )
        fig.map_lower(  # Plot scatterplots in upper half
            sns.kdeplot, **subplot_params
        )
        fig.map_diag(  # Plot scatterplots in diagonal
            sns.histplot, kde=True, **subplot_params
        )

        if fig.legend is not None:
            # position the legend at top right
            fig.legend.set_bbox_to_anchor((1.05, 1))

        self.joint_scatterplot = savefig(fig)

    def _plot_joint_correlation(self):
        """Plot a heatmap of the correlation among all numeric columns."""
        fig = Fig(figsize=(6, 6))
        ax = fig.subplots()
        sns.heatmap(
            self.correlation_df,
            annot=True,
            yticklabels=True,
            mask=np.triu(self.correlation_df),
            ax=ax,
            cmap=self._create_palette(n_colors=self.correlation_df.shape[1]),
        )
        ax.tick_params(rotation=45)
        fig.suptitle("Correlation in Numeric Columns", size=15)

        self.joint_correlation_heatmap = savefig(fig)

    def _get_variable_pairs(self):
        """Get a list of unique pairings of the numeric variables"""
        self.var_pairs = set(combinations(self.correlation_df.columns, r=2))

    def _compare_variable_pairs(self):
        """Get a brief summary of the nature of correlation between pairs of
        numeric variables.
        """
        self._get_variable_pairs()

        for var1, var2 in tqdm(
            self.var_pairs, ncols=99, desc="Bivariate analysis"
        ):
            self._quantify_correlation(var1, var2)
            self._regression_plot(var1, var2)

    def _quantify_correlation(self, var1, var2):
        """Explain the magnitude of correlation between variable pairs.

        :param var1: A numeric column/feature name
        :type var1: str
        :param var2: A numeric column/feature name
        :type var2: str
        """
        correlation = self.correlation_df.loc[var1, var2]
        nature = " positive" if correlation > 0 else " negative"

        value = abs(correlation)
        if value >= 0.9:
            strength = "very strong"
        elif value >= 0.7:
            strength = "strong"
        elif value >= 0.5:
            strength = "moderate"
        elif value >= 0.3:
            strength = "weak"
        elif value >= 0.1:
            strength = "very weak"
        else:
            strength = "virtually no"
            nature = ""

        self.corr_type[
            (var1, var2)
        ] = f"{strength}{ nature} correlation ({correlation:.2f})"

    def _regression_plot(self, var1, var2):
        """Create a scatterplot with a fitted linear regression line.

        :param var1: A numeric column/feature name
        :type var1: str
        :param var2: A numeric column/feature name
        :type var2: str
        """
        fig = Fig(figsize=(8.2, 4))
        ax1, ax2 = fig.subplots(nrows=1, ncols=2)
        # Scatter-plot with linear regression line
        sns.regplot(
            x=var1,
            y=var2,
            data=self.data,
            ax=ax1,
            truncate=False,
            color=self.graph_color,
        )
        # Empirical cummulative distribution function plots
        sns.ecdfplot(
            data=self.data.loc[:, [var1, var2]],
            ax=ax2,
            palette=self._create_palette(n_colors=2),
        )
        ax1.set_title(f"Scatter-plot - {var1} vs {var2}".title(), size=9)
        ax2.set_title("Empirical Cummulative Distribution Functions", size=9)

        self.bivariate_scatterplots[(var1, var2)] = savefig(fig)
