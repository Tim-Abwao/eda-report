import logging
from collections.abc import Iterable
from itertools import combinations
from typing import Sequence, Union

from pandas.core.frame import DataFrame

from eda_report.validate import validate_multivariate_input


class MultiVariable:
    """The defines objects that analyse data with *multiple columns*.

    Input data is held as a :class:`pandas.DataFrame` in order
    to leverage pandas_ built-in statistical methods, as well as functions
    from the `SciPy ecosystem`_.

    .. _pandas: https://pandas.pydata.org/
    .. _SciPy ecosystem: https://www.scipy.org/

    Parameters
    ----------
    data : Iterable
        The data to analyse.

    Example
    -------
    .. literalinclude:: examples.txt
       :lines: 28-57
    """

    def __init__(self, data: Iterable) -> None:
        """Initialise an instance of
        :class:`~eda_report.multivariate.MultiVariable`.
        """
        self.data = validate_multivariate_input(data)

        #: :class:`~pandas.DataFrame`: The *numeric columns* present.
        self.numeric_cols = self._select_cols("number")

        #: :class:`~pandas.DataFrame`: The *categorical columns*. Please note
        #: that **boolean** and **datetime** features are also
        #: **considered categorical** in this context.
        self.categorical_cols = self._select_cols("object", "bool")

        #: :class:`~pandas.DataFrame`: Summary statistics for numeric columns.
        self.numeric_stats = self._compute_numeric_summary_statistics()

        #: :class:`~pandas.DataFrame`: Summary statistics for categorical
        #:  columns.
        self.categorical_stats = self._compute_categorical_summary_statistics()

        #: :class:`~pandas.DataFrame`: Pearson correlation coefficients for the
        #: *numeric columns*.
        self.correlation_df = self._get_correlation()

        #: dict[tuple, str]: Brief descriptions of the nature of correlation
        #: between numeric column pairs.
        self.correlation_descriptions = {}
        self._get_bivariate_analysis()

    def __repr__(self) -> str:
        """Defines the string representation of :class:`Multivariable`.

        Returns
        -------
        str
            The string representation of the ``MultiVariable`` instance.
        """
        # Get a list of numeric features
        numeric_cols = "" if self.numeric_cols is None else self.numeric_cols
        # Get a list of categorical features
        categoric_cols = (
            "" if self.categorical_cols is None else self.categorical_cols
        )
        correlation_description = (
            self._corr_description
            if hasattr(self, "_corr_description")
            else "N/A"
        )
        return "\n".join(
            [
                "\t\t\tOVERVIEW",
                "\t\t\t========",
                f"Numeric features: {', '.join(numeric_cols)}",
                f"Categorical features: {', '.join(categoric_cols)}",
                "\t\t\t  ***",
                "\t  Summary Statistics (Numeric features)",
                "\t  -------------------------------------",
                f"{self.numeric_stats if any(numeric_cols) else 'N/A'}",
                "\t\t\t  ***",
                "\t  Summary Statistics (Categorical features)",
                "\t  -----------------------------------------",
                f"{self.categorical_stats if any(categoric_cols) else 'N/A'}",
                "\t\t\t  ***",
                "\t  Bivariate Analysis (Correlation)",
                "\t  --------------------------------",
                f"{correlation_description}",
            ]
        )

    def describe(self) -> None:
        """Display summary statistics for both numerical and categorical
        columns.
        """
        if self.numeric_stats is None:
            print("\nThere are no numeric columns.\n")
        else:
            print(
                "\n\tSummary Statistics (Numeric columns):\n\n",
                self.numeric_stats,
            )

        if self.categorical_stats is None:
            print("\nThere are no categorical columns.\n")
        else:
            print(
                "\n\tSummary Statistics (Categorical columns):\n\n",
                self.categorical_stats,
            )

    def _select_cols(self, *dtypes: Sequence[str]) -> Union[DataFrame, None]:
        """Get a DataFrame including only the specified ``dtypes``.

        Returns
        -------
        Union[DataFrame, None]
            A dataframe with the desired data types.
        """
        selected_cols = self.data.select_dtypes(include=dtypes)
        return selected_cols if selected_cols.shape[1] > 0 else None

    def _compute_numeric_summary_statistics(self) -> DataFrame:
        """Get descriptive statistics for numeric columns.

        Returns
        -------
        DataFrame
            Numeric summary statistics.
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

    def _compute_categorical_summary_statistics(self) -> DataFrame:
        """Get summary descriptive statistics for categorical columns.

        Returns
        -------
        DataFrame
            Categorical summary statistics.
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
        """Get a DataFrame of the correlation coefficients for numeric
        columns.

        Returns
        -------
        Union[DataFrame, None]
            A dataframe of Pearson correlation coefficients, or None.
        """
        return None if self.numeric_cols is None else self.numeric_cols.corr()

    def _get_variable_pairs(self) -> None:
        """Get a list of unique pairings of the numeric columns."""
        self.var_pairs = set(combinations(self.correlation_df.columns, r=2))

    def _quantify_correlation(self, var1: str, var2: str) -> None:
        """Explain the nature and magnitude of correlation between column
        pairs.

        Parameters
        ----------
        var1, var2 : str
            Numeric column labels.
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

    def _compare_variable_pairs(self) -> None:
        """Get a brief summary of the nature of correlation between pairs of
        numeric columns.
        """
        self._get_variable_pairs()

        for var1, var2 in self.var_pairs:
            self._quantify_correlation(var1, var2)

    def _get_bivariate_analysis(self) -> None:
        """Compare numeric column pairs."""
        if self.numeric_cols is not None and self.numeric_cols.shape[1] > 1:
            self._compare_variable_pairs()
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
                "Skipped Bivariate Analysis: "
                "Not enough numeric variables to compare."
            )
            return None
