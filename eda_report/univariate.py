import seaborn as sns
from eda_report.plotting import Fig, savefig
from pandas.api.types import is_numeric_dtype, is_bool_dtype


class Variable:
    """Blueprint for the structure and properties of each column/variable."""

    def __init__(self, data, graph_colour='cyan'):
        self.data = data
        self.GRAPH_COLOUR = graph_colour
        self.get_data_properties()
        self.get_summary_statictics()

    def get_data_properties(self):
        """Get basic details about the variable's data e.g type & name."""
        self.name = self.data.name
        self.num_unique = self.data.nunique()

        missing_values = self.data.isna().sum()
        if missing_values == 0:
            self.missing = "None"
        else:
            self.missing = \
                f"{missing_values} ({missing_values / len(self.data):.2%})"

        if is_numeric_dtype(self.data):
            if is_bool_dtype(self.data):
                self.var_type = 'categorical'
                self.data = self.data.astype('category')
            else:
                self.var_type = 'numeric'
        else:
            # Handle bool, string and datetime data as categorical
            self.var_type = 'categorical'

    def get_summary_statictics(self):
        """Get summary statistics for the variable as a pandas Series."""
        if self.var_type == 'numeric':
            self._numeric_summary_statictics()
            self._plot_numeric()
        elif self.var_type == 'categorical':
            self._categorical_summary_statictics()
            self._plot_categorical()

    def _numeric_summary_statictics(self):
        """Get summary statistics for a numeric variable."""
        summary = self.data.describe()
        summary.index = [
            'Number of observations', 'Average', 'Standard Deviation',
            'Minimum', 'Lower Quartile', 'Median', 'Upper Quartile', 'Maximum'
        ]
        summary['Skewness'] = self.data.skew()
        summary['Kurtosis'] = self.data.kurt()
        self.statistics = summary.round(7)

    def _categorical_summary_statictics(self):
        """Get summary statistics for a categorical variable."""
        summary = self.data.describe()[['count', 'unique', 'top']]
        summary.index = ['Number of observations', 'Unique values',
                         'Mode (Highest occurring value)']
        self.statistics = summary

        most_common_items = self.data.value_counts().head()
        n = len(self.data)
        self.most_common_items = \
            most_common_items.apply(lambda x: f'{x} ({x / n:.2%})')

    def _plot_numeric(self):
        """Get a boxplot and a histogram for a numeric variable."""
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

        self.graphs = savefig(fig)

    def _plot_categorical(self, color='cyan'):
        """Get a bar-plot for a categorical variable."""
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

        self.graphs = savefig(fig)
