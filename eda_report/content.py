from multiprocessing import Pool
from typing import Any, Dict, Iterable, Optional, Union

from tqdm import tqdm

from eda_report.multivariate import MultiVariable
from eda_report.plotting import _plot_multivariable, _plot_variable
from eda_report.univariate import Variable, _analyze_univariate
from eda_report.validate import validate_groupby_data


class _AnalysisResult:
    """Analyzes data, and stores the resultant summary statistics and graphs.

    Args:
        data (Iterable): The data to analyse.
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        groupby_data (Union[str, int], optional): The column to
            use to group values. Defaults to None.

    """

    def __init__(
        self,
        data: Iterable,
        graph_color: str = "cyan",
        groupby_data: Union[str, int] = None,
    ) -> None:
        self.GRAPH_COLOR = graph_color
        self.multivariable = MultiVariable(data)
        self.GROUPBY_DATA = validate_groupby_data(
            data=self.multivariable.data, groupby_data=groupby_data
        )
        self.univariate_stats = self._get_univariate_statistics()
        self.univariate_graphs = self._get_univariate_graphs()
        self.bivariate_graphs = _plot_multivariable(
            self.multivariable, color=graph_color
        )

    def _get_univariate_statistics(self) -> Dict:
        """Compute summary statistics for all variables present.

        Returns:
            Dict[str, Union[_CategoricalStats, _DatetimeStats, _NumericStats]]:
            Summary statistics.
        """
        data = self.multivariable.data
        with Pool() as p:
            univariate_stats = dict(
                tqdm(
                    p.imap(_analyze_univariate, data.items()),
                    total=data.shape[1],
                    bar_format=(
                        "{desc} {percentage:3.0f}%|{bar:35}| "
                        "{n_fmt}/{total_fmt}"
                    ),
                    desc="Analyze variables: ",
                    dynamic_ncols=True,
                )
            )
        return univariate_stats

    def _get_univariate_graphs(self) -> Dict[str, Dict]:
        """Plot graphs for all variables present.

        Returns:
            Dict[str, Dict]: Univariate graphs.
        """
        with Pool() as p:
            variables_hue_and_color = [
                (stat, self.GROUPBY_DATA, self.GRAPH_COLOR)
                for stat in self.univariate_stats.values()
            ]
            univariate_graphs = dict(
                tqdm(
                    # Plot variables in parallel processes
                    p.imap(_plot_variable, variables_hue_and_color),
                    # Progress-bar options
                    total=len(self.univariate_stats),
                    bar_format=(
                        "{desc} {percentage:3.0f}%|{bar:35}| "
                        "{n_fmt}/{total_fmt}"
                    ),
                    desc="Plot variables:    ",
                    dynamic_ncols=True,
                )
            )
        return univariate_graphs


class _ReportContent(_AnalysisResult):
    """Prepares textual summaries of analysis results.

    Args:
        data (Iterable): The data to analyze.
        title (str, optional): The title to assign the report. Defaults to
            "Exploratory Data Analysis Report".
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        groupby_data (Union[str, int], optional): The column to
            use to group values. Defaults to None.
    """

    def __init__(
        self,
        data: Iterable,
        *,
        title: str = "Exploratory Data Analysis Report",
        graph_color: str = "cyan",
        groupby_data: Union[str, int] = None,
    ) -> None:
        super().__init__(
            data, graph_color=graph_color, groupby_data=groupby_data
        )
        self.TITLE = title
        self.intro_text = self._get_introductory_summary()
        self.variable_info = self._get_variable_info()
        self.bivariate_summaries = self._get_bivariate_summaries()

    def _get_introductory_summary(self) -> str:
        """Get an overview of the number of rows and the nature of columns.

        Returns:
            str: Introduction.
        """
        num_rows, num_cols = self.multivariable.data.shape

        if num_rows == 1:
            rows = "1 row (observation)"
        else:
            rows = f"{num_rows:,} rows (observations)"

        if num_cols == 1:
            cols = "1 column (feature)"
        else:
            cols = f"{num_cols:,} columns (features)"

        # Get numeric column info
        if self.multivariable.numeric_cols is None:
            numeric = ""
        elif self.multivariable.numeric_cols.shape[1] == 1:
            numeric = ", 1 of which is numeric"
        else:
            numeric = (
                f", {self.multivariable.numeric_cols.shape[1]} of which are"
                " numeric"
            )

        return f"The dataset consists of {rows} and {cols}{numeric}."

    def _describe_variable(self, variable: Variable) -> Dict[str, Any]:
        """Get summary statistics for a variable.

        Args:
            univariate_stats (Variable): The data to analyze.

        Returns:
            Dict[str, Any]: Summary statistics.
        """
        if variable.num_unique == 1:
            unique_vals = "1 unique value"
        else:
            unique_vals = f"{variable.num_unique:,} unique values"

        return {
            "description": (
                f"{variable.name.capitalize()} is a {variable.var_type} "
                f"variable with {unique_vals}. {variable.missing} of its "
                "values are missing."
            ),
            "graphs": self.univariate_graphs[variable.name],
            "statistics": (
                variable.summary_statistics._get_summary_statistics()
                .to_frame()
                .round(4)
            ),
            "normality_tests": (
                variable.summary_statistics._test_for_normality()
                if variable.var_type == "numeric"
                else None
            ),
        }

    def _get_variable_info(self) -> Dict[str, Dict]:
        """Get brief descriptions of all columns present in the data.

        Returns:
            Dict[str, Dict]: Summaries of columns present.
        """
        return {
            name: self._describe_variable(stat)
            for name, stat in sorted(self.univariate_stats.items())
        }

    def _get_bivariate_summaries(self) -> Optional[Dict[str, str]]:
        """Get descriptions of the nature of correlation between numeric
        column pairs.

        Returns:
            Optional[Dict[str, str]]: Correlation info.
        """
        if hasattr(self.multivariable, "var_pairs"):
            var_pairs = list(self.multivariable.var_pairs)

            if len(self.multivariable.var_pairs) > 50:
                # Take the top 50 var_pairs by magnitude of correlation.
                var_pairs = (
                    self.multivariable.correlation_df.unstack()[var_pairs]
                    .sort_values(key=abs)
                    .tail(50)
                    .index
                )
            return {
                var_pair: (
                    f"{var_pair[0].title()} and {var_pair[1].title()} have "
                    f"{self.multivariable.correlation_descriptions[var_pair]}."
                )
                for var_pair in var_pairs
            }
        else:
            return None
