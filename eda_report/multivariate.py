import logging
from collections.abc import Iterable
from itertools import combinations
from types import GeneratorType
from typing import Sequence, Union

from pandas.core.frame import DataFrame

from eda_report.univariate import Variable
from eda_report.validate import validate_multivariate_input


class MultiVariable:
    """Defines objects that analyse two-dimensional datasets.

    Input data is held as a :class:`pandas.DataFrame` in order to leverage
    pandas_ built-in statistical methods, as well as functions
    from the `SciPy ecosystem`_.

    .. _pandas: https://pandas.pydata.org/
    .. _SciPy ecosystem: https://www.scipy.org/

    .. note::
       Not meant to be used directly: use the :func:`eda_report.summarize`
       function instead.

    Args:
        data (Iterable): The data to analyse.

    Example:
        .. literalinclude:: examples.txt
           :lines: 85-113
    """

    def __init__(self, data: Iterable) -> None:

        self.data = validate_multivariate_input(data)

        #: :class:`~pandas.DataFrame`: The *numeric columns* present.
        self.numeric_cols = self._select_cols("number")

        #: :class:`~pandas.DataFrame`: The *categorical columns* present.
        self.categorical_cols = self._select_cols("object", "bool")

        #: :class:`~pandas.DataFrame`: Summary statistics for numeric columns.
        self.numeric_stats = self._get_numeric_summary_statistics()

        #: :class:`~pandas.DataFrame`: Summary statistics for categorical
        #:  columns.
        self.categorical_stats = self._get_categorical_summary_statistics()

        #: :class:`~pandas.DataFrame`: Pearson correlation coefficients for the
        #: *numeric columns*.
        self.correlation_df = self._get_correlation()

        #: dict[tuple, str]: Brief descriptions of the nature of correlation
        #: between numeric column pairs.
        self.correlation_descriptions = {}
        self._get_bivariate_analysis()

    def __repr__(self) -> str:
        """Get the string representation of :class:`Multivariable`.

        Returns:
            str: The string representation of the ``MultiVariable`` instance.
        """
        if self.data.shape[1] == 1:
            return str(Variable(self.data.squeeze()).contents)

        if self.numeric_cols is None:
            numeric_info = numeric_stats = ""
        else:
            numeric_info = f"Numeric features: {', '.join(self.numeric_cols)}"
            numeric_stats = (
                "\n\t  Summary Statistics (Numeric features)\n"
                "\t  -------------------------------------\n"
                f"{self.numeric_stats}"
            )

        if self.categorical_cols is None:
            categorical_info = categorical_stats = ""
        else:
            categorical_info = (
                f"Categorical features: {', '.join(self.categorical_cols)}"
            )
            categorical_stats = (
                "\n\t  Summary Statistics (Categorical features)\n"
                "\t  -----------------------------------------\n"
                f"{self.categorical_stats}"
            )
        if hasattr(self, "_corr_description"):
            correlation_description = (
                "\n\t  Bivariate Analysis (Correlation)\n"
                "\t  --------------------------------\n"
                f"{self._corr_description}"
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

    def iter_variables(self) -> GeneratorType:
        """Iterate through all the variables present in alphabetic order.

        Yields:
            GeneratorType: Variables
        """
        for name, data in self.data.sort_index(axis=1).items():
            yield Variable(data=data, name=name)

    def _select_cols(self, *dtypes: Sequence[str]) -> Union[DataFrame, None]:
        """Get a DataFrame including only the specified ``dtypes``.

        Returns:
            Union[DataFrame, None]: A dataframe with the desired data types.
        """
        selected_cols = self.data.select_dtypes(include=dtypes)
        return selected_cols if selected_cols.shape[1] > 0 else None

    def _get_numeric_summary_statistics(self) -> Union[DataFrame, None]:
        """Compute descriptive statistics for numeric columns.

        Returns:
            Union[DataFrame, None]: Numeric summary statistics.
        """
        if self.numeric_cols is not None:
            numeric_stats = self.numeric_cols.describe().T
            numeric_stats["skewness"] = self.numeric_cols.skew(
                numeric_only=True
            )
            numeric_stats["kurtosis"] = self.numeric_cols.kurt(
                numeric_only=True
            )

            return numeric_stats.round(4)
        else:
            return None

    def _get_categorical_summary_statistics(
        self,
    ) -> Union[DataFrame, None]:
        """Compute descriptive statistics for categorical columns.

        Returns:
            Union[DataFrame, None]: Categorical summary statistics.
        """
        if self.categorical_cols is not None:
            categorical_stats = self.categorical_cols.describe().T
            categorical_stats["relative freq"] = (
                categorical_stats["freq"] / len(self.data)
            ).apply(lambda x: f"{x :.2%}")
            return categorical_stats
        else:
            return None

    def _get_correlation(self) -> Union[DataFrame, None]:
        """Get the Pearson correlation coefficients for numeric columns.

        Returns:
            Union[DataFrame, None]: Correlation coefficients
        """
        if self.numeric_cols is None:
            return None
        else:
            unique_ratio = self.numeric_cols.nunique() / len(self.data)
            cols_to_compare = [
                col for col, ratio in unique_ratio.items() if ratio > 0.05
            ]
            if len(cols_to_compare) >= 2:
                return self.numeric_cols[cols_to_compare].corr()
            else:
                return None

    def _quantify_correlation(self, var1: str, var2: str) -> None:
        """Explain the nature and magnitude of correlation between column
        pairs.

        Args:
            var1, var (str): Numeric column labels.
        """
        correlation = self.correlation_df.loc[var1, var2]
        nature = " positive" if correlation > 0 else " negative"

        value = abs(correlation)
        if value >= 0.9:
            strength = "very strong"
        elif value >= 0.7:
            strength = "strong"
        elif value >= 0.5:
            strength = "moderate"
        elif value >= 0.3:
            strength = "weak"
        elif value >= 0.1:
            strength = "very weak"
        else:
            strength = "virtually no"
            nature = ""

        self.correlation_descriptions[
            (var1, var2)
        ] = f"{strength}{ nature} correlation ({correlation:.2f})"

    def _get_bivariate_analysis(self) -> None:
        """Compare numeric column pairs."""
        if self.correlation_df is not None:
            self.var_pairs = set(
                combinations(self.correlation_df.columns, r=2)
            )
            for var1, var2 in self.var_pairs:
                self._quantify_correlation(var1, var2)

            self._corr_description = "\n".join(
                [
                    f"{var_pair[0]} & {var_pair[1]} --> {corr_description}"
                    for var_pair, corr_description in sorted(
                        self.correlation_descriptions.items(),
                        key=lambda x: x[1],
                    )
                ]
            )
        else:
            logging.warning(
                "Skipped Bivariate Analysis: There are less than 2 numeric "
                "variables having > 5% unique values."
            )
            return None
