import logging
from collections.abc import Iterable
from itertools import combinations
from typing import List, Optional, Sequence

from pandas.core.frame import DataFrame

from eda_report.univariate import Variable
from eda_report.validate import validate_multivariate_input


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


def _select_dtypes(
    dataframe: DataFrame, *dtypes: Sequence[str]
) -> Optional[DataFrame]:
    """Get a DataFrame including only the specified `dtypes`.

    Args:
        dataframe (pandas.DataFrame): A 2D array of numeric data.
        *dtypes (str): Data types to include e.g. "bool", "number", etc.

    Returns:
        Optional[DataFrame]: Subset with the desired data types.
    """
    selected_cols = dataframe.select_dtypes(include=dtypes)
    return selected_cols if selected_cols.shape[1] > 0 else None


class MultiVariable:
    """Defines objects that analyze two-dimensional datasets.

    Input data is held as a :class:`pandas.DataFrame` in order to leverage
    pandas_ built-in statistical methods, as well as functions
    from the `SciPy ecosystem`_.

    .. _pandas: https://pandas.pydata.org/
    .. _SciPy ecosystem: https://www.scipy.org/

    .. note::
       Not meant to be used directly: use the :func:`eda_report.summarize`
       function instead.

    Args:
        data (Iterable): The data to analyze.

    Example:
        .. literalinclude:: examples.txt
           :lines: 84-110
    """

    def __init__(self, data: Iterable) -> None:

        self.data = validate_multivariate_input(data)
        self._get_summary_statistics()
        self._get_bivariate_analysis()

    def __repr__(self) -> str:
        """Get the string representation for a ``Multivariable``.

        Returns:
            str: The string representation of the ``MultiVariable`` instance.
        """
        if self.data.shape[1] == 1:
            return str(
                Variable(self.data.squeeze(), name=self.data.columns[0])
            )

        numeric_data = _select_dtypes(self.data, "number")
        if numeric_data is None:
            numeric_info = numeric_stats = ""
        else:
            numeric_info = f"Numeric features: {', '.join(numeric_data)}"
            numeric_stats = (
                "\n\t  Summary Statistics (Numeric features)\n"
                "\t  -------------------------------------\n"
                f"{self._numeric_stats}"
            )

        categorical_data = _select_dtypes(
            self.data, "bool", "category", "object"
        )
        if categorical_data is None:
            categorical_info = categorical_stats = ""
        else:
            categorical_info = (
                f"Categorical features: {', '.join(categorical_data)}"
            )
            categorical_stats = (
                "\n\t  Summary Statistics (Categorical features)\n"
                "\t  -----------------------------------------\n"
                f"{self._categorical_stats}"
            )
        if hasattr(self, "_correlation_descriptions"):
            max_pairs = min(20, len(self._correlation_descriptions))
            top_20 = list(self._correlation_descriptions.items())[:max_pairs]
            corr_repr = "\n".join(
                [
                    f"{var_pair[0]} & {var_pair[1]} --> {corr_description}"
                    for var_pair, corr_description in top_20
                ]
            )
            correlation_description = (
                f"\n\t  Pearson's Correlation (Top 20)"
                "\n\t  ------------------------------\n"
                f"{corr_repr}"
            )
        else:
            correlation_description = ""

        return "\n".join(
            [
                "\t\t\tOVERVIEW",
                "\t\t\t========",
                f"{numeric_info}",
                f"{categorical_info}",
                f"{numeric_stats}",
                f"{categorical_stats}",
                f"{correlation_description}",
            ]
        )

    def _get_summary_statistics(self) -> None:
        """Compute descriptive statistics."""
        numeric_data = _select_dtypes(self.data, "number")
        if numeric_data is None:
            self._numeric_stats = None
        else:
            numeric_stats = numeric_data.describe().T
            numeric_stats["skewness"] = numeric_data.skew(numeric_only=True)
            numeric_stats["kurtosis"] = numeric_data.kurt(numeric_only=True)
            self._numeric_stats = numeric_stats.round(4)

        categorical_data = _select_dtypes(
            self.data, "category", "object", "bool"
        )
        if categorical_data is None:
            self._categorical_stats = None
        else:
            categorical_stats = categorical_data.describe().T
            categorical_stats["relative freq"] = (
                categorical_stats["freq"] / len(self.data)
            ).apply(lambda x: f"{x :.2%}")
            self._categorical_stats = categorical_stats

    def _get_correlation_descriptions(self) -> None:
        """Get brief descriptions of the nature of correlation between numeric
        column pairs."""
        self._correlation_descriptions = {
            pair: _describe_correlation(corr_value)
            for pair, corr_value in self._correlation_values
        }

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
