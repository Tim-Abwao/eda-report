from collections.abc import Iterable
from textwrap import shorten
from typing import Optional

from pandas import DataFrame, Series
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)

from eda_report.validate import validate_univariate_input


class Variable:
    """Creates objects that describe the general properties of one-dimensional
    datasets, such as data type and missing values.

    Input data is internally held as a :class:`~pandas.Series` in order
    to leverage pandas_ built-in statistical methods, as well as functions
    from the `SciPy ecosystem`_.

    .. _pandas: https://pandas.pydata.org/
    .. _SciPy ecosystem: https://www.scipy.org/


    Parameters
    ----------
    data : Iterable
        The data to analyse.
    name : Optional[str]
        The name to assign the ``Variable``, by default None.

    Example
    --------

    .. literalinclude:: examples.txt
       :lines: 63-83
    """

    def __init__(self, data: Iterable, *, name: str = None) -> None:
        self.data = validate_univariate_input(data, name=name)

        #: Optional[str]: The ``Variable``'s *name*. If no name is specified
        #: during instantiation, the name will be equal to the value of the
        #: ``name`` attribute of the input data (if present), or None.
        self.name = self.data.name

        #: str: The ``Variable``'s *type* — one of *"boolean"*,
        #: *"categorical"*, *"datetime"* or *"numeric"*.
        self.var_type = self._get_variable_type()

        #: int: The *number of unique values* present in the ``Variable``.
        self.num_unique = self.data.nunique()

        #: list: The *unique values* present in the ``Variable``.
        self.unique = sorted(self.data.dropna().unique())

        #: str: The number of *missing values* in the form
        #: ``number (percentage%)`` e.g "4 (16.67%)".
        self.missing = self._get_missing_values_info()

    def rename(self, name: Optional[str] = None) -> None:
        """Rename the ``Variable`` as specified.

        Parameters
        ----------
        name
            The name to assign to the ``Variable``, by default None.
        """
        self.name = self.data.name = name
        if hasattr(self, "most_common_items"):
            self.most_common_items.set_axis([name], axis=1, inplace=True)

    def _get_variable_type(self) -> str:
        """Determine the ``Variable``'s type.

        Returns
        -------
        var_type : {"boolean", "categorical", "datetime", "numeric"}
        """
        if is_numeric_dtype(self.data):
            if is_bool_dtype(self.data) or set(self.data.dropna()) == {0, 1}:
                # Consider boolean data as categorical
                self.data = self.data.astype("category")
                return "boolean"
            elif self.data.nunique() / len(self.data) <= 0.1:
                # Consider numeric data with <= 10% unique values categorical
                self.data = self.data.astype("category").cat.as_ordered()
                return "categorical"
            else:
                return "numeric"
        elif is_datetime64_any_dtype(self.data):
            return "datetime"
        else:
            # If 1/3 or less of the values are unique, use categorical
            if (self.data.nunique() / self.data.shape[0]) <= (1 / 3):
                self.data = self.data.astype("category")
            else:
                self.data = self.data.astype("object")

            return "categorical"

    def _get_missing_values_info(self) -> str:
        """Get the number of missing values in the ``Variable``.

        Returns
        -------
        str
            Details about the number of missing values.
        """
        missing_values = self.data.isna().sum()
        if missing_values == 0:
            return None
        else:
            return (
                f"{missing_values:,} ({missing_values / len(self.data):.2%})"
            )


class CategoricalVariable(Variable):
    def __init__(self, data: Iterable, *, name: str = None) -> None:
        super().__init__(data, name=name)

        #: :class:`~pandas.DataFrame`: The ``Variables`` *Summary statistics*.
        self.statistics = self._get_summary_statistics()

    def __repr__(self) -> str:
        """Get the string representation of the ``Variable``.

        Returns
        -------
        str
            A summary of the ``Variable``'s properties.
        """
        return "\n".join(
            [
                "\t\tOverview",
                "\t\t========",
                f"Name: {self.name}",
                f"Type: {self.var_type}",
                f"Number of Observations: {len(self.data)}",
                "Unique Values: "
                + f"{shorten(f'{self.num_unique} -> {self.unique}', 60)}",
                f"Missing Values: {self.missing}\n",
                "\t  Most Common Items",
                "\t  -----------------",
                f"{self._get_most_common().to_frame(name='')}",
            ]
        )

    def _get_summary_statistics(self) -> None:
        """Get summary statistics for the column/feature."""
        return self.data.describe().set_axis(
            [
                "Number of observations",
                "Unique values",
                "Mode (Most frequent)",
                "Maximum frequency",
            ],
            axis=0,
        )

    def _get_most_common(self) -> Series:
        # Get most common items and their relative frequency (%)
        most_common_items = self.data.value_counts().head()
        n = len(self.data)
        return most_common_items.apply(lambda x: f"{x:,} ({x / n:.2%})")


class DatetimeVariable(Variable):
    def __init__(self, data: Iterable, *, name: str = None) -> None:
        super().__init__(data, name=name)

    def __repr__(self) -> str:
        """Get the string representation of the ``DatetimeVariable``.

        Returns
        -------
        str
            A summary of the ``DatetimeVariable``'s properties.
        """
        return "\n".join(
            [
                "\t\tOverview",
                "\t\t========",
                f"Name: {self.name}",
                f"Type: {self.var_type}",
                f"Number of Observations: {len(self.data)}",
                f"Missing Values: {self.missing}\n",
                "\t  Summary Statistics",
                "\t  ------------------",
                f"{self._get_summary_statistics().to_frame(name='')}",
            ]
        )

    def _get_summary_statistics(self) -> DataFrame:
        """Get summary statistics for the column/feature."""
        return self.data.describe(datetime_is_numeric=True).set_axis(
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


class NumericVariable(Variable):
    def __init__(self, data: Iterable, *, name: str = None) -> None:
        super().__init__(data, name=name)
        #: :class:`~pandas.DataFrame`: The ``NumericVariables`` *Summary
        #: statistics*.
        self.statistics = self._get_summary_statistics()

    def __repr__(self) -> str:
        """Get the string representation of the ``Variable``.

        Returns
        -------
        str
            A summary of the ``NumericVariable``'s properties.
        """
        return "\n".join(
            [
                "\t\tOverview",
                "\t\t========",
                f"Name: {self.name}",
                f"Type: {self.var_type}",
                "Unique Values: "
                + f"{shorten(f'{self.num_unique} -> {self.unique}', 60)}",
                f"Missing Values: {self.missing}\n",
                "\t  Summary Statistics",
                "\t  ------------------",
                f"{self._get_summary_statistics().to_frame(name='')}",
            ]
        )

    def _get_summary_statistics(self) -> DataFrame:
        """Get summary statistics for the column/feature."""
        summary_stats = self.data.describe().set_axis(
            [
                "Number of observations",
                "Average",
                "Standard Deviation",
                "Minimum",
                "Lower Quartile",
                "Median",
                "Upper Quartile",
                "Maximum",
            ]
        )
        summary_stats["Skewness"] = self.data.skew()
        summary_stats["Kurtosis"] = self.data.kurt()

        return summary_stats

    def _test_for_normality(self):
        pass
