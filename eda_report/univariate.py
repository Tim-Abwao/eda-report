from collections.abc import Iterable
from textwrap import shorten
from typing import Dict, Optional, Tuple

from pandas import DataFrame, Series
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)
from scipy import stats

from eda_report.validate import validate_univariate_input


class Variable:

    """Defines objects that analyze one-dimensional datasets to obtain summary
    statistics, and evaluate properties such as data type and missing values.

    Input data is internally held as a :class:`~pandas.Series` in order
    to leverage pandas_ built-in statistical methods, as well as functions
    from the `SciPy ecosystem`_.

    .. _pandas: https://pandas.pydata.org/
    .. _SciPy ecosystem: https://www.scipy.org/

    Args:
        data (Iterable): The data to analyze.
        name (str, optional): The name to assign the variable. Defaults to
            None.

    Examples:
        .. literalinclude:: examples.txt
           :lines: 6-22
        .. literalinclude:: examples.txt
           :lines: 26-53
        .. literalinclude:: examples.txt
           :lines: 57-76
    """

    def __init__(self, data: Iterable, *, name: str = None) -> None:
        data = validate_univariate_input(data, name=name)

        #: Optional[str]: The variable's *name*. If no name is specified
        #: during instantiation, the name will be equal to the value of the
        #: ``name`` attribute of the input data (if present), or None.
        self.name = data.name

        #: str: The variable's *type* — one of *"boolean"*, *"categorical"*,
        #: *"datetime"*, *"numeric"* or *"numeric (<10 levels)"*.
        self.var_type = self._get_variable_type(data)

        #: int: The *number of unique values* present in the variable.
        self.num_unique = data.nunique()

        #: list: The *unique values* present in the variable.
        self.unique_values = sorted(data.dropna().unique())

        #: str: The number of *missing values* in the form
        #: ``number (percentage%)`` e.g "4 (16.67%)".
        self.missing = self._get_missing_values_info(data)
        self._num_non_null = len(data.dropna())

        #: pandas.Series: Descriptive statistics
        self.summary_stats = self._get_summary_statistics(data)
        self._normality_test_results = self._test_for_normality(data)

    def __repr__(self) -> str:
        """Get the string representation of a variable based on it's summary
        statistics.

        Returns:
            str: Summary statistics.
        """
        sample_values = shorten(
            f"{self.num_unique} -> {self.unique_values}", 60
        )
        basic_details = "\n".join(
            [
                f"\nName: {self.name}",
                f"Type: {self.var_type}",
                f"Non-null Observations: {self._num_non_null}",
                f"Unique Values: {sample_values}",
                f"Missing Values: {self.missing}\n",
                "\t\t  Summary Statistics",
                "\t\t  ------------------",
            ]
        )
        if self.var_type == "numeric":
            summary_stats = "\n".join(
                [
                    f"\t{key + ':':21} {value :>15.4f}"
                    for key, value in self.summary_stats.items()
                ]
            )
            normality_test_results = "\n".join(
                [
                    "\n\t\t  Tests for Normality",
                    "\t\t  -------------------",
                    f"{self._normality_test_results}",
                ]
            )
            return "\n".join(
                [basic_details, summary_stats, normality_test_results]
            )
        else:
            summary_stats = "\n".join(
                [
                    f"\t{key + ':':21} {str(value):>15}"
                    for key, value in self.summary_stats.items()
                ]
            )
            return "\n".join([basic_details, summary_stats])

    def _get_variable_type(self, data: Series) -> str:
        """Determine the variable type.

        Returns:
            str: The variable type.
        """
        if is_numeric_dtype(data):
            if is_bool_dtype(data) or set(data.dropna()) == {0, 1}:
                # Consider boolean data as categorical
                return "boolean"
            elif data.nunique() <= 10:
                # Consider numeric data with <= 10 unique values categorical
                return "numeric (<10 levels)"
            else:
                return "numeric"
        elif set(data.dropna()) in [{False, True}, {"No", "Yes"}, {"N", "Y"}]:
            return "boolean"
        elif is_datetime64_any_dtype(data):
            return "datetime"

        else:
            return "categorical"

    def _get_missing_values_info(self, data: Series) -> Optional[str]:
        """Get the number of values missing from the variable.

        Returns:
            Optional[str]: Details about the number of missing values.
        """
        missing_values = data.isna().sum()
        if missing_values == 0:
            return None
        else:
            return f"{missing_values:,} ({missing_values / len(data):.2%})"

    def _get_summary_statistics(self, data: Series) -> Dict:
        """Compute summary statistics for the variable based on data type."""
        if self.var_type == "numeric":
            stats = data.describe()
            return {
                "Average": stats["mean"],
                "Standard Deviation": stats["std"],
                "Minimum": stats["min"],
                "Lower Quartile": stats["25%"],
                "Median": stats["50%"],
                "Upper Quartile": stats["75%"],
                "Maximum": stats["max"],
                "Skewness": data.skew(),
                "Kurtosis": data.kurt(),
            }
        elif self.var_type == "datetime":
            stats = data.describe()
            return {
                "Average": stats["mean"],
                "Minimum": stats["min"],
                "Lower Quartile": stats["25%"],
                "Median": stats["50%"],
                "Upper Quartile": stats["75%"],
                "Maximum": stats["max"],
            }
        else:
            data = data.copy().astype("category")
            stats = data.describe()
            return {
                "Mode (Most frequent)": stats["top"],
                "Maximum frequency": stats["freq"],
            }

    def _test_for_normality(
        self, data: Series, alpha: float = 0.05
    ) -> DataFrame:
        """Perform the "D'Agostino's K-squared", "Kolmogorov-Smirnov" and
        "Shapiro-Wilk" tests for normality.

        Args:
            alpha (float, optional): The level of significance. Defaults to
                0.05.

        Returns:
            pandas.DataFrame: Table of results.
        """
        data = data.dropna()
        if self.var_type == "numeric":
            # The scipy implementation of the Shapiro-Wilk test reports:
            # "For N > 5000 the W test statistic is accurate but the p-value
            # may not be."
            shapiro_sample = data.sample(5000) if len(data) > 5000 else data
            tests = [
                "D'Agostino's K-squared test",
                "Kolmogorov-Smirnov test",
                "Shapiro-Wilk test",
            ]
            p_values = [
                stats.normaltest(data).pvalue,
                stats.kstest(data, "norm", N=200).pvalue,
                stats.shapiro(shapiro_sample).pvalue,
            ]
            results = DataFrame(index=tests)
            results["p-value"] = [f"{x:.7f}" for x in p_values]
            results[f"Conclusion at α = {alpha}"] = [
                "Possibly normal"
                if p_value > alpha
                else "Unlikely to be normal"
                for p_value in p_values
            ]
            return results
        else:
            return None

    def rename(self, name: str) -> None:
        self.name = name


def _analyze_univariate(name_and_data: Tuple) -> Variable:
    """Helper function to concurrently analyze data with multiprocessing."""
    name, data = name_and_data
    var = Variable(data, name=name)

    return name, var
