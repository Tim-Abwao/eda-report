from textwrap import shorten

from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)

from eda_report.validate import validate_univariate_input


class Variable:
    """This is the blueprint for objects that analyse and plot one-dimensional
    datasets: a *single column/feature*.
    """

    def __init__(
        self, data, *, graph_color="orangered", name=None, target_data=None
    ):
        """Initialise an instance of :class:`Variable`.

        :param data: The data to process.
        :type data: array-like, sequence, iterable.
        :param graph_color: The color to apply to the graphs created,
            defaults to 'orangered'.
        :type graph_color: str, optional
        :param name: The feature's name.
        :type name: str, optional
        :param target_data: Data for the target variable (dependent
            feature). Currently used to group and color-code values in graphs.
        :type target_data: array-like, optional
        """
        self.data = validate_univariate_input(data)
        #: The *name* of the *column/feature*. If unspecified in the ``name``
        #: argument during instantiation, this will be taken as the value of
        #: the ``name`` attribute of the input data.
        self.name = self._get_name(name)
        #: The *type* of feature; either *boolean*, *categorical*, *datetime*
        #:  or *numeric*.
        self.var_type = self._get_variable_type()
        #: *Summary statistics* for the *column/feature*, as a
        #: :class:`pandas.DataFrame`.
        self.statistics = self._get_summary_statistics()
        #: The *number of unique values* present in the *column/feature*.
        self.num_unique = self.data.nunique()
        #: The set of *unique values* present in the *column/feature*.
        self.unique = set(self.data.unique())
        #: The number of *missing values*.
        self.missing = self._get_missing_values()
        #: The *color* applied to the created graphs.
        self.graph_color = graph_color
        self.TARGET_DATA = validate_univariate_input(target_data)

    def __repr__(self):
        """Creates the string representation for :class:`Variable` objects."""
        return f"""\
            Overview
            ========
Name: {self.name},
Type: {self.var_type},
Unique Values: {shorten(f'{self.num_unique} -> {self.unique}', 60)},
Missing Values: {self.missing}

        Summary Statistics
        ==================
{self.statistics}
"""

    def _get_name(self, name=None):
        """Set the feature's name.

        :param name: The name to give the feature, defaults to None
        :type name: str, optional
        """
        if name:
            self.data = self.data.rename(name)

        return self.data.name

    def _get_variable_type(self):
        """Get the variable type: 'categorical' or 'numeric'."""
        if is_numeric_dtype(self.data):
            if is_bool_dtype(self.data) or set(self.data.dropna()) == {0, 1}:
                return "boolean"
            else:
                # Only int and float types
                return "numeric"
        elif is_datetime64_any_dtype(self.data):
            self.data = self.data.dt.strftime("%c")
            return "datetime"
        else:
            # Handle str, etc as categorical
            return "categorical"

    def _get_summary_statistics(self):
        """Get summary statistics for the column/feature."""
        if self.var_type == "numeric":
            return self._numeric_summary_statictics()
        elif self.var_type in {"boolean", "categorical", "datetime"}:
            if (self.data.shape[0] / self.data.nunique()) > 1.5:
                # If less than 2-thirds of the values are unique
                self.data = self.data.astype("category")
            else:
                self.data = self.data.astype("object")
            return self._categorical_summary_statistics()

    def _numeric_summary_statictics(self):
        """Get summary statistics for a numeric column/feature."""
        summary = self.data.describe()
        summary.index = [
            "Number of observations",
            "Average",
            "Standard Deviation",
            "Minimum",
            "Lower Quartile",
            "Median",
            "Upper Quartile",
            "Maximum",
        ]
        summary["Skewness"] = self.data.skew()
        summary["Kurtosis"] = self.data.kurt()

        return summary.round(7).to_frame()

    def _categorical_summary_statistics(self):
        """Get summary statistics for a categorical column/feature."""
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
            lambda x: f"{x} ({x / n:.2%})"
        ).to_frame()

        return summary.to_frame()

    def _get_missing_values(self):
        """Get the number of missing values in the column/feature."""
        missing_values = self.data.isna().sum()
        if missing_values == 0:
            return "None"
        else:
            return f"{missing_values} ({missing_values / len(self.data):.2%})"
