import seaborn as sns
import numpy as np
from itertools import combinations
from eda_report.plotting import Fig, savefig
from eda_report.validate import validate_input_dtype
from tqdm import tqdm


class MultiVariable:
    """The blueprint for containers to hold data with multiple columns
    (features).
    """

    def __init__(self, data, graph_colour='orangered'):
        """Initialise an instance of :class:`MultiVariable`.

        :param data: The data to process, ideally a ``pandas.DataFrame``
            with mutliple columns.
        :type data: An array-like, sequence, iterable or dict
        :param graph_colour: The colour to apply to the graphs created,
            defaults to 'orangered'.
        :type graph_colour: str, optional
        """
        self.data = validate_input_dtype(data)
        self.GRAPH_COLOUR = graph_colour
        #: A ``DataFrame`` of the numeric columns present in the data
        self.numeric_cols = self._select_cols('number')
        #: A ``DataFrame`` of the categorical columns present in the data
        self.categotical_cols = self._select_cols('object', 'bool')
        #: A ``DataFrame`` of correlation coefficients for the numeric columns
        self.correlation_df = self._get_correlation()
        self.get_bivariate_analysis()

    def _get_bivariate_analysis(self):
        """Compare numeric variable pairs.
        """
        if self.numeric_cols.size > 1:
            self._plot_joint_scatterplot()
            self._plot_joint_correlation()
            self._compare_variable_pairs()

    def _select_cols(self, *dtypes):
        """Get a DataFrame of the numeric columns present.

        :param dtype: The column data type to include.
        :type dtype: str
        :return: A ``DataFrame`` with columns of the specified data type, or
            ``None`` if no column is of that data type.
        :rtype: A ``DataFrame``, or ``None``
        """
        selected_cols = self.data.select_dtypes(include=dtypes)
        return selected_cols if selected_cols.shape[1] > 0 else None

    def _plot_joint_scatterplot(self):
        """Create a joint scatter-plot of all numeric columns.
        """
        fig = sns.pairplot(
            self.numeric_cols, height=1.75,
            plot_kws={'color': self.GRAPH_COLOUR},
            diag_kws={'color': self.GRAPH_COLOUR}
        )
        fig.fig.suptitle('Scatter-plots of Numeric Columns', x=0.5, y=1.04,
                         size=20)
        self.joint_scatterplot = savefig(fig)

    def _plot_joint_correlation(self):
        """Plot a heatmap of the correlation in all numeric columns."""
        fig = Fig(figsize=(6, 6))
        ax = fig.subplots()
        sns.heatmap(self.correlation_df, annot=True, yticklabels=True,
                    mask=np.triu(self.correlation_df), ax=ax,
                    cmap=sns.light_palette(self.GRAPH_COLOUR, as_cmap=True))
        ax.tick_params(rotation=45)
        fig.suptitle('Correlation in Numeric Columns', size=15)

        self.joint_correlation_plot = savefig(fig)

    def _get_correlation(self):
        """Get a DataFrame of the correlation coefficients for numeric
        columns.
        """
        return None if self.numeric_cols is None else self.data.corr()

    def _get_variable_pairs(self):
        """Get a list of unique pairings of the numeric variables"""
        self.var_pairs = set(combinations(self.correlation_df.columns, r=2))

    def _regression_plot(self, var1, var2):
        """Create a scatterplot with a fitted linear regression line.

        Parameters:
        ----------
        var1, var2: string
            A pair of numeric column(variable) names.
        """
        fig = Fig(figsize=(8.2, 4))
        ax1, ax2 = fig.subplots(1, 2)
        sns.regplot(x=var1, y=var2, data=self.data, ax=ax1, truncate=False,
                    color=self.GRAPH_COLOUR)
        sns.regplot(x=var2, y=var1, data=self.data, ax=ax2, truncate=False,
                    color=self.GRAPH_COLOUR)
        ax1.set_title(f'Scatterplot - {var1} vs {var2}'.title(), size=9)
        ax2.set_title(f'Scatterplot - {var2} vs {var1}'.title(), size=9)

        self.bivariate_scatterplots[(var1, var2)] = savefig(fig)

    def _quantify_correlation(self, var1, var2):
        """Explain the magnitude of correlation between variable pairs.

        Parameters:
        ----------
        var1, var2: string
            A pair of numeric column(variable) names.
        """
        correlation = self.correlation_df.loc[var1, var2]
        nature = ' positive' if correlation > 0 else ' negative'

        value = abs(correlation)
        if value >= 0.9:
            strength = 'very strong'
        elif value >= 0.7:
            strength = 'strong'
        elif value >= 0.5:
            strength = 'moderate'
        elif value >= 0.3:
            strength = 'weak'
        elif value >= 0.1:
            strength = 'very weak'
        else:
            strength = 'virtually no'
            nature = ''

        self.corr_type[(var1, var2)] = \
            f'{strength}{ nature} correlation ({correlation:.2f})'

    def _compare_variable_pairs(self):
        """
        Get a brief summary of the nature of correlation between pairs of
        numeric variables.
        """
        self._get_variable_pairs()
        self.corr_type = {}
        self.bivariate_scatterplots = {}

        for var1, var2 in tqdm(self.var_pairs, ncols=79):
            self._quantify_correlation(var1, var2)
            self._regression_plot(var1, var2)
