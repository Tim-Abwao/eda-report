from multiprocessing import Pool
from typing import Any, Dict, Iterable, Optional, Union

import pandas as pd
from tqdm import tqdm

from eda_report.multivariate import MultiVariable
from eda_report.plotting import _plot_multivariable, _plot_variable
from eda_report.univariate import Variable, _analyze_univariate
from eda_report.validate import validate_groupby_data


def _get_contingency_tables(
    categorical_df: pd.DataFrame, groupby_data: pd.Series
) -> Dict[str, pd.DataFrame]:
    """Get contingency tables for categorical columns.

    Args:
        categorical_df (pandas.DataFrame): Categorical data.
        groupby_data (pandas.Series): Values to group by.

    Returns:
        Dict[str, pd.DataFrame]: Contingency tables for each column.
    """
    if (categorical_df is None) or (groupby_data is None):
        return {}
    contingency_tables = {
        col: pd.crosstab(
            categorical_df[col],
            groupby_data,
            margins=True,
            margins_name="Total",
        )
        for col in categorical_df
    }
    # Exclude groupby data in case it is among the categorical cols
    contingency_tables.pop(groupby_data.name, None)
    return contingency_tables


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
        self.analyzed_variables = self._analyze_variables()
        self.univariate_stats = self._get_univariate_statistics()
        self.contingency_tables = _get_contingency_tables(
            self.multivariable.data[
                [
                    col_name
                    for col_name, var in self.analyzed_variables.items()
                    if var.var_type != "numeric"
                ]
            ],
            self.GROUPBY_DATA,
        )
        self.normality_tests = self._test_for_normality()
        self.univariate_graphs = self._get_univariate_graphs()
        self.bivariate_graphs = _plot_multivariable(
            self.multivariable, color=graph_color
        )
        self.bivariate_summaries = self._get_bivariate_summaries()

    def _analyze_variables(self) -> Dict[str, Variable]:
        """Compute summary statistics and assess variable properties.

        Returns:
            Dict[str, Variable]: Univariate analysis results.
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

    def _get_univariate_statistics(self) -> Dict[str, pd.DataFrame]:
        """Get a dataframe of summary statistics for all variables.

        Returns:
            Dict[str, pandas.DataFrame]: Summary statistics.
        """
        return {
            name: variable.summary_statistics._get_summary_statistics()
            .to_frame()
            .round(4)
            for name, variable in self.analyzed_variables.items()
        }

    def _test_for_normality(self) -> Dict[str, pd.DataFrame]:
        """Perform tests for normality.

        Returns:
            Dict[str, pandas.DataFrame]: Normality test results.
        """
        return {
            name: variable.summary_statistics._test_for_normality()
            for name, variable in self.analyzed_variables.items()
            if variable.var_type == "numeric"
        }

    def _get_univariate_graphs(self) -> Dict[str, Dict]:
        """Plot graphs for all variables present.

        Returns:
            Dict[str, Dict]: Univariate graphs.
        """
        with Pool() as p:
            variables_hue_and_color = [
                (variable, self.GROUPBY_DATA, self.GRAPH_COLOR)
                for variable in self.analyzed_variables.values()
            ]
            univariate_graphs = dict(
                tqdm(
                    # Plot variables in parallel processes
                    p.imap(_plot_variable, variables_hue_and_color),
                    # Progress-bar options
                    total=len(self.analyzed_variables),
                    bar_format=(
                        "{desc} {percentage:3.0f}%|{bar:35}| "
                        "{n_fmt}/{total_fmt}"
                    ),
                    desc="Plot variables:    ",
                    dynamic_ncols=True,
                )
            )
        return univariate_graphs

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
        self.variable_descriptions = self._describe_variables()

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

    def _describe_variables(self) -> Dict[str, Any]:
        """Get summary statistics for a variable.

        Args:
            univariate_stats (Variable): The data to analyze.

        Returns:
            Dict[str, Any]: Summary statistics.
        """
        descriptions = {}
        for name, variable in self.analyzed_variables.items():
            if variable.num_unique == 1:
                unique_vals = "1 unique value"
            else:
                unique_vals = f"{variable.num_unique:,} unique values"

            descriptions[name] = (
                f"{variable.name.capitalize()} is a {variable.var_type} "
                f"variable with {unique_vals}. {variable.missing} of its "
                "values are missing."
            )
        return descriptions
