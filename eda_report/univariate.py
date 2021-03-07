import seaborn as sns
from eda_report.plotting import Fig, savefig
from pandas.api.types import is_numeric_dtype, is_bool_dtype


class Variable:
    """This is the blueprint for structures to hold the contents and
        characteristics of each column(variable) in a dataset.
    """

    def __init__(self, data, graph_colour='orangered', name=None):
        """Initialise an instance of :class:`Variable`.

        :param data: The data to process.
        :type data: ``pandas.Series``
        :param graph_colour: The colour to apply to the graphs created,
            defaults to 'orangered'.
        :type graph_colour: str, optional
        :param name: The name to give the variable.
        :type name: str, optional
        """
        self.data = data
        #: The name of the variable.
        self.name = name if name is not None else self.data.name
        #: The variable's type.
        self.var_type = self._get_variable_type()
        #: Summary statistics for the variable, as a ``pandas.Series``.
        self.statistics = self._get_summary_statictics()
        #: The number of unique values in the variable.
        self.num_unique = self.data.nunique()
        #: Unique values in the variable.
        self.unique = self.data.unique()
        #: The number of missing values.
        self.missing = self._get_missing_values()
        #: The colour to apply to the created graphs.
        self.GRAPH_COLOUR = graph_colour
        #: The graphs for the variable as bytes in a file-like object.
        self.graphs = self._plot_graphs()

    def _get_missing_values(self):
        """Get the number of missing values in the data.
        """
        missing_values = self.data.isna().sum()
        if missing_values == 0:
            return "None"
        else:
            return f"{missing_values} ({missing_values / len(self.data):.2%})"

    def _get_variable_type(self):
        """Get the variable type: 'categorical' or 'numeric'.
        """
        if is_numeric_dtype(self.data):
            if is_bool_dtype(self.data):
                self.data = self.data.astype('category')
                return 'categorical'
            else:
                return 'numeric'
        else:
            # Handle bool, string and datetime data as categorical
            return 'categorical'

    def _get_summary_statictics(self):
        """Get summary statistics for the variable as a pandas Series.
        """
        if self.var_type == 'numeric':
            return self._numeric_summary_statictics()
        elif self.var_type == 'categorical':
            return self._categorical_summary_statictics()

    def _plot_graphs(self):
        """Plot graphs for the variable, based on variable type.
        """
        if self.var_type == 'numeric':
            return self._plot_numeric()
        elif self.var_type == 'categorical':
            return self._plot_categorical()

    def _numeric_summary_statictics(self):
        """Get summary statistics for a numeric variable.
        """
        summary = self.data.describe()
        summary.index = [
            'Number of observations', 'Average', 'Standard Deviation',
            'Minimum', 'Lower Quartile', 'Median', 'Upper Quartile', 'Maximum'
        ]
        summary['Skewness'] = self.data.skew()
        summary['Kurtosis'] = self.data.kurt()
        return summary.round(7)

    def _categorical_summary_statictics(self):
        """Get summary statistics for a categorical variable.
        """
        summary = self.data.describe()[['count', 'unique', 'top']]
        summary.index = ['Number of observations', 'Unique values',
                         'Mode (Highest occurring value)']

        most_common_items = self.data.value_counts().head()
        n = len(self.data)
        self.most_common_items = \
            most_common_items.apply(lambda x: f'{x} ({x / n:.2%})')
        return summary

    def _plot_numeric(self):
        """Get a boxplot and a histogram for a numeric variable.
        """
        fig = Fig(figsize=(6, 6), linewidth=1)
        ax1, ax2 = fig.subplots(2, 1)
        # Box-plot
        ax1.boxplot(self.data.dropna(), vert=False, notch=True)
        ax1.set_yticklabels([''])
        ax1.set_xlabel(f'{self.name}')
        ax1.set_title(f'Box-plot of {self.name}', size=12)
        # Histogram
        ax2.set_title(f'Distribution plot of {self.name}', size=12)
        sns.histplot(x=self.data, kde=True, ax=ax2, color=self.GRAPH_COLOUR)

        return savefig(fig)

    def _plot_categorical(self, color='cyan'):
        """Get a bar-plot for a categorical variable.
        """
        fig = Fig(figsize=(6, 4), linewidth=1)
        ax = fig.subplots()

        self.data.value_counts().nlargest(10).plot.bar(
            color=self.GRAPH_COLOUR, ax=ax
        )
        ax.tick_params(axis='x', rotation=45)
        ax.set_title(f'Bar-plot of {self.name}', size=12)

        # Annotate bars
        for p in ax.patches:
            ax.annotate(f'{p.get_height():,}', ha='left',
                        xy=(p.get_x(), p.get_height()*1.02),)

        return savefig(fig)
