from multiprocessing import Pool
from typing import Any, Dict, Iterable, Optional, Tuple, Union

from pandas import Series
from tqdm import tqdm

from eda_report.multivariate import MultiVariable
from eda_report.plotting import BivariatePlots, UnivariatePlots
from eda_report.univariate import (
    CategoricalStats,
    DatetimeStats,
    NumericStats,
    analyze_univariate,
)
from eda_report.validate import validate_target_variable


class AnalysisResult:
    """Analyzes data, and stores the resultant summary statistics and graphs.

    Args:
        data (Iterable): The data to analyse.
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        target_variable (Union[str, int], optional): The column to
            use to group values. Defaults to None.

    """

    def __init__(
        self,
        data: Iterable,
        graph_color: str = "cyan",
        target_variable: Union[str, int] = None,
    ) -> None:
        self.GRAPH_COLOR = graph_color
        self.multivariable = MultiVariable(data)
        self.TARGET_VARIABLE = validate_target_variable(
            data=self.multivariable.data, target_variable=target_variable
        )
        self.univariate_stats = self._get_univariate_statistics()
        self.univariate_graphs = self._get_univariate_graphs()
        self.bivariate_graphs = BivariatePlots(
            self.multivariable,
            graph_color=self.GRAPH_COLOR,
            hue=self.TARGET_VARIABLE,
        ).graphs

    def _analyze_variable(
        self, items: Tuple[str, Series]
    ) -> Tuple[str, Union[CategoricalStats, DatetimeStats, NumericStats]]:
        """Get summary statistics for a single variable.

        Args:
            items (Tuple[str, Series]): Pair returned by
                :func:`pandas.DataFrame.iteritems`.

        Returns:
            Tuple[str, Union[CategoricalStats, DatetimeStats, NumericStats]]:
            Variable name, and summary statistics.
        """
        name, data = items
        return name, analyze_univariate(data, name=name)

    def _get_univariate_statistics(
        self,
    ) -> Dict[str, Union[CategoricalStats, DatetimeStats, NumericStats]]:
        """Compute summary statistics for all variables present.

        Returns:
            Dict[str, Union[CategoricalStats, DatetimeStats, NumericStats]]:
            Summary statistics.
        """
        data = self.multivariable.data
        with Pool() as p:
            univariate_stats = dict(
                tqdm(
                    p.imap(self._analyze_variable, data.iteritems()),
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
        variables = [stat.variable for stat in self.univariate_stats.values()]
        return UnivariatePlots(
            variables, graph_color=self.GRAPH_COLOR, hue=self.TARGET_VARIABLE
        ).graphs


class ReportContent(AnalysisResult):
    """Prepares textual summaries of analysis results.

    Args:
        data (Iterable): The data to analyze.
        title (str, optional): The title to assign the report. Defaults to
            "Exploratory Data Analysis Report".
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        target_variable (Union[str, int], optional): The column to
            use to group values. Defaults to None.
    """

    def __init__(
        self,
        data: Iterable,
        *,
        title: str = "Exploratory Data Analysis Report",
        graph_color: str = "cyan",
        target_variable: Union[str, int] = None,
    ) -> None:
        super().__init__(
            data, graph_color=graph_color, target_variable=target_variable
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

    def _describe_variable(
        self,
        univariate_stat: Union[CategoricalStats, DatetimeStats, NumericStats],
    ) -> Dict[str, Any]:
        """Get summary statistics for a variable.

        Args:
            univariate_stats (Variable): The data to analyze.

        Returns:
            Dict[str, Any]: Summary statistics.
        """
        variable = univariate_stat.variable
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
            "statistics": univariate_stat._get_summary_statistics().to_frame(),
            "normality_tests": (
                univariate_stat._test_for_normality()
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
            return {
                var_pair: (
                    f"{var_pair[0].title()} and {var_pair[1].title()} have "
                    f"{self.multivariable.correlation_descriptions[var_pair]}."
                )
                for var_pair in self.multivariable.var_pairs
            }
        else:
            return None
