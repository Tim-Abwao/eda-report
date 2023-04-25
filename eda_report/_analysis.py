from multiprocessing import Pool
from typing import Dict, Iterable, Optional, Union

import pandas as pd
from tqdm import tqdm

from eda_report._validate import _validate_groupby_variable
from eda_report.bivariate import Dataset
from eda_report.plotting import _plot_dataset, _plot_variable
from eda_report.univariate import Variable, _analyze_univariate


def _get_contingency_tables(
    categorical_df: pd.DataFrame, groupby_data: pd.Series
) -> Dict[str, pd.DataFrame]:
    """Get contingency tables for categorical variables.

    Args:
        categorical_df (pandas.DataFrame): Categorical data.
        groupby_data (pandas.Series): Values to group by.

    Returns:
        Dict[str, pandas.DataFrame]: Contingency tables for each column.
    """
    if (categorical_df.shape[1] == 0) or (groupby_data is None):
        return {}

    contingency_tables = {
        col: pd.crosstab(
            index=categorical_df[col],
            columns=groupby_data,
            margins=True,
            margins_name="Total",
        )
        for col in categorical_df
        # Only include columns with upto 20 unique values to cut clutter
        if categorical_df[col].nunique() <= 20
    }
    # Exclude groupby_variable in case it is among the categorical cols
    contingency_tables.pop(groupby_data.name, None)
    return contingency_tables


class _AnalysisResult:
    """Analyzes data, and stores the resultant summary statistics and graphs.

    Args:
        data (Iterable): The data to analyse.
        graph_color (str, optional): The color to apply to the graphs.
            Defaults to "cyan".
        groupby_variable (Union[str, int], optional): The column to
            use to group values. Defaults to None.
    """

    def __init__(
        self,
        data: Iterable,
        graph_color: str = "cyan",
        groupby_variable: Union[str, int] = None,
    ) -> None:
        self.GRAPH_COLOR = graph_color
        self.dataset = Dataset(data)
        self.GROUPBY_DATA = _validate_groupby_variable(
            data=self.dataset.data, groupby_variable=groupby_variable
        )
        self.variables = self._analyze_variables()
        self.univariate_stats = self._get_univariate_statistics()
        self.normality_tests = self._get_normality_test_results()
        self.univariate_graphs = self._get_univariate_graphs()
        self.bivariate_graphs = _plot_dataset(self.dataset, color=graph_color)
        self.bivariate_summaries = self._get_bivariate_summaries()

    def _analyze_variables(self) -> Dict[str, Variable]:
        """Compute summary statistics and assess variable properties.

        Returns:
            Dict[str, Variable]: Univariate analysis results.
        """
        data = self.dataset.data
        with Pool() as p:
            univariate_stats = dict(
                tqdm(
                    # Analyze variables concurrently
                    p.imap(_analyze_univariate, data.items()),
                    # Progress-bar options
                    total=data.shape[1],
                    bar_format=(
                        "{desc} {percentage:3.0f}%|{bar:35}| "
                        "{n_fmt}/{total_fmt}"
                    ),
                    desc="Analyze variables: ",
                    dynamic_ncols=True,
                )
            )
        # Create contingency tables
        categorical_cols = [
            col_name
            for col_name, var in univariate_stats.items()
            if var.var_type != "numeric"
        ]
        self.contingency_tables = _get_contingency_tables(
            data[categorical_cols], self.GROUPBY_DATA
        )
        return univariate_stats

    def _get_univariate_statistics(self) -> Dict[str, pd.DataFrame]:
        """Get a dataframe of summary statistics for all variables.

        Returns:
            Dict[str, pandas.DataFrame]: Summary statistics.
        """
        return {
            name: variable.summary_stats
            for name, variable in self.variables.items()
        }

    def _get_normality_test_results(self) -> Dict[str, pd.DataFrame]:
        """Perform tests for normality.

        Returns:
            Dict[str, pandas.DataFrame]: Normality test results.
        """
        return {
            name: variable._normality_test_results
            for name, variable in self.variables.items()
            if variable.var_type == "numeric"
        }

    def _get_univariate_graphs(self) -> Dict[str, Dict]:
        """Plot graphs for all variables present.

        Returns:
            Dict[str, Dict]: Univariate graphs.
        """
        with Pool() as p:
            data = self.dataset.data
            variable_data_hue_and_color = [
                (
                    variable,
                    data[variable.name],
                    self.GROUPBY_DATA,
                    self.GRAPH_COLOR,
                )
                for variable in self.variables.values()
            ]
            univariate_graphs = dict(
                tqdm(
                    # Plot variables in parallel processes
                    p.imap(_plot_variable, variable_data_hue_and_color),
                    # Progress-bar options
                    total=len(self.variables),
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
        if self.dataset._correlation_values is None:
            return None
        else:
            # Take the top 20 pairs by magnitude of correlation.
            # 20 var_pairs ≈ 10+ pages
            # 20 numeric columns == 190 var_pairs ≈ 95+ pages.
            pairs_to_include = [
                pair for pair, _ in self.dataset._correlation_values[:20]
            ]
            correlation_descriptions = self.dataset._correlation_descriptions
            return {
                var_pair: (
                    f"{var_pair[0].title()} and {var_pair[1].title()} have "
                    f"{correlation_descriptions[var_pair]}."
                )
                for var_pair in pairs_to_include
            }
