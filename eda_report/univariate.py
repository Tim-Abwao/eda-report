from collections.abc import Iterable
from textwrap import shorten
from typing import Optional, Union

from pandas import DataFrame, Series
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)
from scipy import stats

from eda_report.validate import validate_univariate_input


class Variable:

    """Defines objects that evaluate the general properties of one-dimensional
    datasets, such as data type and missing values.

    Input data is internally held as a :class:`~pandas.Series` in order
    to leverage pandas_ built-in statistical methods, as well as functions
    from the `SciPy ecosystem`_.

    .. _pandas: https://pandas.pydata.org/
    .. _SciPy ecosystem: https://www.scipy.org/

    Args:
        data (Iterable): The data to analyze.
        name (str, optional): The name to assign the variable. Defaults to
            None.
    """

    def __init__(self, data: Iterable, *, name: str = None) -> None:
        self.data = validate_univariate_input(data, name=name)

        #: Optional[str]: The variable's *name*. If no name is specified
        #: during instantiation, the name will be equal to the value of the
        #: ``name`` attribute of the input data (if present), or None.
        self.name = self.data.name

        #: str: The variable's *type* — one of *"boolean"*, *"categorical"*,
        #: *"datetime"*, *"numeric"* or *"numeric (<10 levels)"*.
        self.var_type = self._get_variable_type()

        #: int: The *number of unique values* present in the variable.
        self.num_unique = self.data.nunique()

        #: list: The *unique values* present in the variable.
        self.unique = sorted(self.data.dropna().unique())

        #: str: The number of *missing values* in the form
        #: ``number (percentage%)`` e.g "4 (16.67%)".
        self.missing = self._get_missing_values_info()

    def rename(self, name: str = None) -> None:
        """Rename the variable as specified.

        Args:
            name (str, optional): The name to assign to the variable.
                Defaults to None.
        """
        self.name = self.data.name = name

    def _get_variable_type(self) -> str:
        """Determine the variable type.

        Returns:
            str: The variable type.
        """
        if is_numeric_dtype(self.data):
            if is_bool_dtype(self.data) or set(self.data.dropna()) == {0, 1}:
                # Consider boolean data as categorical
                self.data = self.data.astype("category")
                return "boolean"
            elif self.data.nunique() <= 10:
                # Consider numeric data with <= 10 unique values categorical
                self.data = self.data.astype("category").cat.as_ordered()
                return "numeric (<10 levels)"
            else:
                return "numeric"

        elif is_datetime64_any_dtype(self.data):
            return "datetime"
        elif (self.data.nunique() / self.data.shape[0]) <= (1 / 3):
            # If 1/3 or less of the values are unique, use categorical
            self.data = self.data.astype("category")
        else:
            self.data = self.data.astype("object")
        return "categorical"

    def _get_missing_values_info(self) -> Optional[str]:
        """Get the number of values missing from the variable.

        Returns:
            Optional[str]: Details about the number of missing values.
        """
        missing_values = self.data.isna().sum()
        if missing_values == 0:
            return None
        else:
            return (
                f"{missing_values:,} ({missing_values / len(self.data):.2%})"
            )


class CategoricalStats:
    """Get descriptive statistics for a categorical ``Variable``.

    .. note::
       Not meant to be used directly: use the :func:`eda_report.summarize`
       function instead.

    Args:
        variable (Variable): The data to analyze.

    Example:
        .. literalinclude:: examples.txt
           :lines: 6-23
    """

    def __init__(self, variable: Variable) -> None:
        self.variable = variable

    def __repr__(self) -> str:
        """Get the string representation of the analysis results.

        Returns:
            str: Summary statistics.
        """
        sample_values = shorten(
            f"{self.variable.num_unique} -> {self.variable.unique}", 60
        )
        return "\n".join(
            [
                "\t\tOverview",
                "\t\t========",
                f"Name: {self.variable.name}",
                f"Type: {self.variable.var_type}",
                f"Number of Observations: {len(self.variable.data)}",
                f"Unique Values: {sample_values}",
                f"Missing Values: {self.variable.missing}\n",
                "\t  Most Common Items",
                "\t  -----------------",
                f"{self._get_most_common().to_frame(name='')}",
            ]
        )

    def _get_summary_statistics(self) -> Series:
        """Calculate summary statistics.

        Returns:
            :class:`~pandas.Series`: Summary statistics.
        """
        return self.variable.data.describe().set_axis(
            [
                "Number of observations",
                "Unique values",
                "Mode (Most frequent)",
                "Maximum frequency",
            ],
            axis=0,
        )

    def _get_most_common(self) -> Series:
        """Get most common items and their relative frequency (%).

        Returns:
            :class:`~pandas.Series`: Top 5 items by frequency.
        """
        most_common_items = self.variable.data.value_counts().head()
        n = len(self.variable.data)
        return most_common_items.apply(lambda x: f"{x:,} ({x / n:.2%})")


class DatetimeStats:
    """Get descriptive statistics for a datetime ``Variable``.

    .. note::
       Not meant to be used directly: use the :func:`eda_report.summarize`
       function instead.

    Args:
        variable (Variable): The data to analyze.

    Example:
        .. literalinclude:: examples.txt
           :lines: 27-46
    """

    def __init__(self, variable: Variable) -> None:
        self.variable = variable

    def __repr__(self) -> str:
        """Get the string representation of the analysis results.

        Returns:
            str: Summary statistics.
        """
        return "\n".join(
            [
                "\t\tOverview",
                "\t\t========",
                f"Name: {self.variable.name}",
                f"Type: {self.variable.var_type}",
                f"Number of Observations: {len(self.variable.data)}",
                f"Missing Values: {self.variable.missing}\n",
                "\t  Summary Statistics",
                "\t  ------------------",
                f"{self._get_summary_statistics().to_frame(name='')}",
            ]
        )

    def _get_summary_statistics(self) -> Series:
        """Calculate summary statistics.

        Returns:
            :class:`~pandas.Series`: Summary statistics.
        """
        return self.variable.data.describe(datetime_is_numeric=True).set_axis(
            [
                "Number of observations",
                "Average",
                "Minimum",
                "Lower Quartile",
                "Median",
                "Upper Quartile",
                "Maximum",
            ],
            axis=0,
        )


class NumericStats:
    """Get descriptive statistics for a numeric ``Variable``.

    .. note::
       Not meant to be used directly: use the :func:`eda_report.summarize`
       function instead.

    Args:
        variable (Variable): The data to analyze.

    Example:
        .. literalinclude:: examples.txt
           :lines: 50-78
    """

    def __init__(self, variable) -> None:
        self.variable = variable

    def __repr__(self) -> str:
        """Get the string representation of the analysis results.

        Returns:
            str: Summary statistics.
        """
        sample_values = shorten(
            f"{self.variable.num_unique} -> {self.variable.unique}", 60
        )
        return "\n".join(
            [
                "\t\tOverview",
                "\t\t========",
                f"Name: {self.variable.name}",
                f"Type: {self.variable.var_type}",
                f"Unique Values: {sample_values}",
                f"Missing Values: {self.variable.missing}\n",
                "\t  Summary Statistics",
                "\t  ------------------",
                f"{self._get_summary_statistics().to_frame(name='')}\n",
                "\t  Tests for Normality",
                "\t  -------------------",
                f"{self._test_for_normality()}",
            ]
        )

    def _get_summary_statistics(self) -> Series:
        """Calculate summary statistics.

        Returns:
            :class:`~pandas.Series`: Summary statistics.
        """
        summary_stats = self.variable.data.describe().set_axis(
            [
                "Number of observations",
                "Average",
                "Standard Deviation",
                "Minimum",
                "Lower Quartile",
                "Median",
                "Upper Quartile",
                "Maximum",
            ],
            axis=0,
        )
        summary_stats["Skewness"] = self.variable.data.skew()
        summary_stats["Kurtosis"] = self.variable.data.kurt()

        return summary_stats

    def _test_for_normality(self, alpha: float = 0.05) -> DataFrame:
        """Perform the "D'Agostino's K-squared", "Kolmogorov-Smirnov" and
        "Shapiro-Wilk" tests for normality.

        Args:
            alpha (float, optional): The level of significance. Defaults to
                0.05.

        Returns:
            :class:`~pandas.DataFrame`: Table of results.
        """
        data = self.variable.data.dropna()
        # The scikit-learn implementation of the Shapiro-Wilk test reports:
        # "For N > 5000 the W test statistic is accurate but the p-value may
        # not be."
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
        conclusion = f"Conclusion at α = {alpha}"
        results = DataFrame(
            {
                "p-value": p_values,
                conclusion: [p_value > alpha for p_value in p_values],
            },
            index=tests,
        )
        results[conclusion] = results[conclusion].map(
            {
                True: "Possibly normal",
                False: "Unlikely to be normal",
            }
        )
        results["p-value"] = results["p-value"].apply(lambda x: f"{x:.7f}")
        return results


def analyze_univariate(
    data: Iterable, *, name: str = None
) -> Union[CategoricalStats, DatetimeStats, NumericStats]:
    """Convert a one-dimensional dataset into a
    :class:`~eda_report.univariate.Variable`, and get summary statistics.

    Args:
        data (Iterable): The data to analyze.
        name (str, optional): The name to assign the variable. Defaults to
            None.

    Returns:
        Union[CategoricalStats, DatetimeStats, NumericStats]: Summary
        statistics
    """
    var = Variable(data, name=name)
    if var.var_type == "numeric":
        return NumericStats(variable=var)
    elif var.var_type == "datetime":
        return DatetimeStats(variable=var)
    else:
        return CategoricalStats(variable=var)
