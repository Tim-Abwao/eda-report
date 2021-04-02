import seaborn as sns
from pandas.api.types import is_bool_dtype, is_numeric_dtype
from PIL import Image
from scipy.stats import probplot

from eda_report.plotting import Fig, savefig
from eda_report.validate import validate_univariate_input


class Variable:
    """This is the blueprint for structures to hold the contents and
    characteristics of *individual columns/features*.
    """

    def __init__(self, data, graph_color='orangered', name=None):
        """Initialise an instance of :class:`Variable`.

        :param data: The data to process.
        :type data: ``pandas.Series``
        :param graph_color: The color to apply to the graphs created,
            defaults to 'orangered'.
        :type graph_color: str, optional
        :param name: The feature's name.
        :type name: str, optional
        """
        self.data = validate_univariate_input(data)
        #: The *name* of the *column/feature*. If unspecified in the name
        #: argument during instantiation, this will be taken as the value of
        #: the ``name`` attribute of the input data.
        self.name = name if name is not None else self.data.name
        #: The *column/feature*'s *type*; either *categorical* or *numeric*.
        self.var_type = self._get_variable_type()
        #: *Summary statistics* for the *column/feature*, as a
        #: ``pandas.DataFrame``.
        self.statistics = self._get_summary_statictics()
        #: The *number of unique values* in the *column/feature*.
        self.num_unique = self.data.nunique()
        #: The *unique values* in the *column/feature*.
        self.unique = self.data.unique()
        #: The number of *missing values* (``NaN``, ``None``, ``NA``, ...).
        self.missing = self._get_missing_values()
        #: The *color* applied to the created graphs.
        self.graph_color = graph_color
        # Get graphs for the column/feature as a dict of file-like objects.
        self._graphs = self._plot_graphs()

    def show_graphs(self):
        """Display the graphs for the *column/feature* using the :class:`PIL.Image`
        class.
        """
        for graph in self._graphs.values():
            image = Image.open(graph)
            image.show()

    def _get_missing_values(self):
        """Get the number of missing values in the **column/feature**.
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
        """Get summary statistics for the column/feature as a pandas Series.
        """
        if self.var_type == 'numeric':
            return self._numeric_summary_statictics()
        elif self.var_type == 'categorical':
            return self._categorical_summary_statictics()

    def _plot_graphs(self):
        """Plot graphs for the column/feature, based on variable type.
        """
        if self.var_type == 'numeric':
            return {
                'hist_and_boxplot': self._plot_histogram_and_boxplot(),
                'qq_plot': self._plot_qq_plot(),
                'run_plot': self._plot_run_plot()
            }
        elif self.var_type == 'categorical':
            return {
                'bar_plot': self._plot_bar()
            }

    def _numeric_summary_statictics(self):
        """Get summary statistics for a numeric column/feature.
        """
        summary = self.data.describe()
        summary.index = [
            'Number of observations', 'Average', 'Standard Deviation',
            'Minimum', 'Lower Quartile', 'Median', 'Upper Quartile', 'Maximum'
        ]
        summary['Skewness'] = self.data.skew()
        summary['Kurtosis'] = self.data.kurt()
        return summary.round(7).to_frame()

    def _categorical_summary_statictics(self):
        """Get summary statistics for a categorical column/feature.
        """
        summary = self.data.describe()[['count', 'unique', 'top']]
        summary.index = ['Number of observations', 'Unique values',
                         'Mode (Highest occurring value)']

        most_common_items = self.data.value_counts().head()
        n = len(self.data)
        self.most_common_items = \
            most_common_items.apply(lambda x: f'{x} ({x / n:.2%})').to_frame()
        return summary.to_frame()

    def _plot_histogram_and_boxplot(self):
        """Get a boxplot and a histogram for a numeric column/feature.
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
        sns.histplot(x=self.data, kde=True, ax=ax2, color=self.graph_color)

        return savefig(fig)

    def _plot_qq_plot(self):
        """Get a quantile-quantile probability plot for a numeric column/
        feature.
        """
        # Create a figure and axes
        fig = Fig(figsize=(6, 4), linewidth=1)
        ax = fig.subplots()
        # Get quantile data.
        theoretical_quantiles, ordered_values = probplot(
            self.data,
            fit=False  # The OLS line of best fit will be plotted in regplot
        )
        # Plot the data and a line of best fit
        sns.regplot(x=theoretical_quantiles, y=ordered_values, ax=ax,
                    color=self.graph_color)
        ax.set_title(f'Q-Q Plot (Probability Plot) of {self.name}', size=12)
        ax.set_xlabel('Theoretical Quantiles (~ Standard Normal)')
        ax.set_ylabel('Ordered Values')

        return savefig(fig)

    def _plot_run_plot(self):
        """Get a run sequence plot / line plot for a numeric column/feature.
        """
        # Create a figure and axes
        fig = Fig(figsize=(6, 4), linewidth=1)
        ax = fig.subplots()
        # Get a line plot of the data
        ax.plot(self.data, marker='.', color=self.graph_color)

        xmin = self.data.index[0]
        xmax = self.data.index[-1]
        p50 = self.data.quantile(0.5)
        p5, p95 = self.data.quantile(0.05), self.data.quantile(0.95)
        # Plot a horizontal line at the 50th percentile
        ax.hlines(p50, xmin, xmax, 'grey', '--')
        ax.text(xmax, p50, ' Median')
        # Plot a horizontal line at the 5th percentile
        ax.hlines(p5, xmin, xmax, 'grey', '--')
        ax.text(xmax, p5, ' $5^{th}$ Percentile')
        # Plot a horizontal lines at the 95th percentile
        ax.hlines(p95, xmin, xmax, 'grey', '--')
        ax.text(xmax, p95, ' $95^{th}$ Percentile')

        ax.tick_params(axis='x', rotation=45)  # rotate x-labels by 45°
        ax.set_title(f'Line Plot (Run Plot) of {self.name}', size=12)
        ax.set_ylabel('Observed Value')
        ax.set_xlabel('Index')

        return savefig(fig)

    def _plot_bar(self, color='cyan'):
        """Get a bar-plot for a categorical column/feature.
        """
        fig = Fig(figsize=(6, 4), linewidth=1)
        ax = fig.subplots()

        self.data.value_counts().nlargest(10).plot.bar(
            color=self.graph_color, ax=ax
        )
        ax.tick_params(axis='x', rotation=45)
        ax.set_title(f'Bar-plot of {self.name}', size=12)

        # Annotate bars
        for p in ax.patches:
            ax.annotate(f'{p.get_height():,}', ha='left',
                        xy=(p.get_x(), p.get_height()*1.02),)

        return savefig(fig)
