import logging
from collections.abc import Iterable
from itertools import combinations
from textwrap import indent
from typing import List

from pandas import DataFrame

from eda_report._validate import _validate_dataset


def _compute_correlation(dataframe: DataFrame) -> List:
    """Get the Pearson correlation coefficients for numeric variables.

    Args:
        dataframe (pandas.DataFrame): A 2D array of numeric data.

    Returns:
        Optional[List]: A list of column pairs and their Pearson's correlation
        coefficients; sorted by magnitude in descending order.
    """
    if dataframe is None:
        return None

    numeric_data = dataframe.select_dtypes("number")
    if numeric_data.shape[1] < 2:
        return None
    else:
        correlation_df = numeric_data.corr(method="pearson")
        unique_pairs = list(combinations(correlation_df.columns, r=2))
        correlation_info = [
            (pair, correlation_df.at[pair]) for pair in unique_pairs
        ]
        return sorted(correlation_info, key=lambda x: -abs(x[1]))


def _describe_correlation(corr_value: float) -> str:
    """Explain the nature and magnitude of correlation.

    Args:
        corr_value (str): Pearson's correlation coefficient.

    Returns:
        str: Brief description of correlation type.
    """
    nature = " positive" if corr_value > 0 else " negative"
    value = abs(corr_value)
    if value >= 0.8:
        strength = "very strong"
    elif value >= 0.6:
        strength = "strong"
    elif value >= 0.4:
        strength = "moderate"
    elif value >= 0.2:
        strength = "weak"
    elif value >= 0.05:
        strength = "very weak"
    else:
        strength = "virtually no"
        nature = ""
    return f"{strength}{ nature} correlation ({corr_value:.2f})"


class Dataset:
    """Analyze two-dimensional datasets to obtain descriptive statistics
    and correlation information.

    Input data is stored as a :class:`pandas.DataFrame` in order to leverage
    pandas_' built-in statistical methods.

    .. _pandas: https://pandas.pydata.org/

    Args:
        data (Iterable): The data to analyze.

    Example:
        .. literalinclude:: examples.txt
           :lines: 79-101
    """

    def __init__(self, data: Iterable) -> None:
        self.data = _validate_dataset(data)
        self._get_summary_statistics()
        self._get_bivariate_analysis()

    def __repr__(self) -> str:
        """Get the string representation for a `Dataset`.

        Returns:
            str: The string representation of the `Dataset` instance.
        """
        if self._numeric_stats is None:
            numeric_stats = ""
        else:
            numeric_stats_title = (
                "Summary Statistics for Numeric features "
                f"({self._numeric_stats.shape[0]})"
            )
            numeric_stats = "\n".join(
                [
                    f"\n\t\t  {numeric_stats_title}",
                    f"\t\t  {'-' * len(numeric_stats_title)}",
                    indent(f"{self._numeric_stats}\n", "  "),
                ]
            )

        if self._categorical_stats is None:
            categorical_stats = ""
        else:
            categorical_stats_title = (
                "Summary Statistics for Categorical features "
                f"({self._categorical_stats.shape[0]})"
            )
            categorical_stats = "\n".join(
                [
                    f"\t{categorical_stats_title}",
                    f"\t{'-' * len(categorical_stats_title)}",
                    indent(f"{self._categorical_stats}\n", " " * 4),
                ]
            )
        if hasattr(self, "_correlation_descriptions"):
            max_pairs = min(20, len(self._correlation_descriptions))
            top_20 = list(self._correlation_descriptions.items())[:max_pairs]
            corr_repr = "\n".join(
                [
                    f"{var_pair[0] + ' & ' + var_pair[1]:>32} -> "
                    f"{corr_description}"
                    for var_pair, corr_description in top_20
                ]
            )
            correlation_description = "\n".join(
                [
                    "\n\t\t\tPearson's Correlation (Top 20)",
                    f"\t\t\t{'-' * 30}",
                    f"{corr_repr}",
                ]
            )
        else:
            correlation_description = ""

        return "\n".join(
            [
                f"{numeric_stats}",
                indent(f"{categorical_stats}", "\t"),
                f"{correlation_description}",
                "\t",
            ]
        )

    def _get_summary_statistics(self) -> None:
        """Compute descriptive statistics."""
        data = self.data.copy()
        numeric_data = data.select_dtypes("number")
        # Consider numeric columns with < 11 unique values as categorical
        categorical_with_numbers = [
            col for col in numeric_data if numeric_data[col].nunique() < 11
        ]
        numeric_data = numeric_data.drop(columns=categorical_with_numbers)
        if numeric_data.shape[1] < 1:
            self._numeric_stats = None
        else:
            numeric_stats = numeric_data.describe().T
            numeric_stats["count"] = numeric_stats["count"].astype("int")
            numeric_stats = numeric_stats.rename(
                columns={"mean": "avg", "std": "stddev"}
            )
            numeric_stats["skewness"] = numeric_data.skew(numeric_only=True)
            numeric_stats["kurtosis"] = numeric_data.kurt(numeric_only=True)
            self._numeric_stats = numeric_stats.round(4)

        categorical_data = data.drop(columns=numeric_data.columns).copy()
        if categorical_data.shape[1] < 1:
            self._categorical_stats = None
        else:
            for col in categorical_data:
                # Convert categorical columns with "unique ratio" < 0.3 to
                # categorical dtype, which would consume much less memory.
                if (
                    categorical_data[col].nunique() / len(categorical_data)
                ) < 0.3:
                    categorical_data[col] = categorical_data[col].astype(
                        "category"
                    )
                else:
                    categorical_data[col] = categorical_data[col].astype(
                        "string"
                    )
            categorical_stats = categorical_data.describe().T
            categorical_stats["relative freq"] = (
                categorical_stats["freq"] / len(self.data)
            ).apply(lambda x: f"{x :.2%}")
            self._categorical_stats = categorical_stats

    def _get_bivariate_analysis(self) -> None:
        """Compare numeric column pairs."""
        self._correlation_values = _compute_correlation(self.data)
        if self._correlation_values is None:
            logging.warning(
                "Skipped Bivariate Analysis: There are less than 2 numeric "
                "variables."
            )
        else:
            self._get_correlation_descriptions()

    def _get_correlation_descriptions(self) -> None:
        """Get brief descriptions of the nature of correlation between numeric
        column pairs."""
        self._correlation_descriptions = {
            pair: _describe_correlation(corr_value)
            for pair, corr_value in self._correlation_values
        }
