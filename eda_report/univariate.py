from collections.abc import Iterable
from textwrap import shorten
from typing import Optional

from pandas import DataFrame
from pandas.api.types import (is_bool_dtype, is_datetime64_any_dtype,
                              is_numeric_dtype)

from eda_report.validate import validate_univariate_input


class Variable:
    """This defines objects for analysing one-dimensional datasets.

    The input data is internally handled as a :class:`~pandas.Series` in order
    to leverage pandas_ built-in statistical methods, as well as functions
    from the `SciPy ecosystem`_.

    .. _pandas: https://pandas.pydata.org/
    .. _SciPy ecosystem: https://www.scipy.org/

    The result is a concise summary of the data's statistical properties.

    Parameters
    ----------
    data : Iterable
        The data to analyse.
    name : Optional[str]
        The name to assign the ``Variable``, by default None.

    Example
    --------

    .. literalinclude:: examples.txt
       :lines: 3-23
    """

    def __init__(self, data: Iterable, *, name: str = None) -> None:
        """Initialise an instance of :class:`~eda_report.univariate.Variable`.
        """
        self.data = validate_univariate_input(data, name=name)

        #: Optional[str]: The ``Variable``'s *name*. If no name is specified
        #: during instantiation, the name will be equal to the value of the
        #: ``name`` attribute of the input data (if present), or None.
        self.name = self.data.name

        #: str: The ``Variable``'s *type* — one of *"boolean"*,
        #: *"categorical"*, *"datetime"* or *"numeric"*.
        self.var_type = self._get_variable_type()

        #: :class:`~pandas.DataFrame`: The ``Variables`` *Summary statistics*.
        self.statistics = self._get_summary_statistics()

        #: int: The *number of unique values* present in the ``Variable``.
        self.num_unique = self.data.nunique()

        #: list: The *unique values* present in the ``Variable``.
        self.unique = sorted(self.data.dropna().unique())

        #: str: *Missing value information* in the form
        #: ``number (percentage%)``.
        self.missing = self._get_missing_values_info()

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
                "Unique Values: "
                + f"{shorten(f'{self.num_unique} -> {self.unique}', 60)}",
                f"Missing Values: {self.missing}",
                "\t\t  ***",
                "\t  Summary Statistics",
                f"{self.statistics}",
            ]
        )

    def rename(self, name: Optional[str] = None) -> None:
        """Rename the ``Variable`` as specified.

        Parameters
        ----------
        name
            The name to assign to the ``Variable``, by default None.
        """
        self.name = self.data.name = name
        self.statistics.set_axis([name], axis=1, inplace=True)
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
                return "boolean"
            else:
                return "numeric"
        elif is_datetime64_any_dtype(self.data):
            self.data = self.data.dt.strftime("%c")
            return "datetime"
        else:
            # Handle object, string, etc as categorical
            return "categorical"

    def _get_summary_statistics(self) -> DataFrame:
        """Get summary statistics for the column/feature."""
        if self.var_type == "numeric":
            summary = self.data.describe().set_axis(
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
            summary["Skewness"] = self.data.skew()
            summary["Kurtosis"] = self.data.kurt()

            return summary.round(7).to_frame()

        else:  # {"boolean", "categorical", "datetime"}
            if (self.data.shape[0] / self.data.nunique()) > 1.5:
                # If less than 2-thirds of the values are unique
                self.data = self.data.astype("category")
            else:
                self.data = self.data.astype("object")

            summary = self.data.describe()[["count", "unique", "top"]]
            summary.index = [
                "Number of observations",
                "Unique values",
                "Mode (Highest occurring value)",
            ]

            # Get most common items and their relative frequency (%)
            most_common_items = self.data.value_counts().head()
            n = len(self.data)
            self.most_common_items = most_common_items.apply(
                lambda x: f"{x:,} ({x / n:.2%})"
            ).to_frame()

            return summary.to_frame()

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
            return f"{missing_values:,} ({missing_values / len(self.data):.2%})"
