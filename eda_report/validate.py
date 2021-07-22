import logging
from typing import Union

from pandas import DataFrame, RangeIndex, Series

from eda_report.exceptions import InputError


def clean_column_names(data):
    """Makes sure that *columns/features* have *meaningful* names.

    When an array/sequence/iterable is used to create a ``DataFrame``
    but no column names are specified, ``pandas`` by default names the columns
    by index as [0, 1, 2, ...] ( :class:`~pandas.RangeIndex` ).

    This function renames such columns to ['var_1', 'var_2, 'var_3', ...],
    making references and comparisons much more intuitive.

    :param data: The data whose columns are checked
    :type data: :class:`pandas.DataFrame`.
    """
    # Ensure the data has meaningful column names
    if isinstance(data.columns, RangeIndex):
        data.columns = [f"var_{i+1}" for i in data.columns]

    return data


def warn_if_target_data_has_high_cardinality(
    target_data: Series, threshold: int = 10
) -> None:
    """Check whether the ``target_data`` is suitable for color-coding or has
    too many unique values (> ``threshold``).

    Parameters
    ----------
    target_data : Series
        The data intended to color-code graphs.
    threshold : int, optional
        Maximum allowable cardinality, by default 10
    """
    if target_data.nunique() > threshold:
        logging.warning(
            f"Target variable '{target_data.name}' not used to color-code "
            "graphs since it has high cardinality "
            f"({target_data.nunique()}) which would clutter graphs."
        )


def validate_multivariate_input(data):
    """Ensures that *multivariate input data* is of type :class:`pandas.DataFrame`.

    If it isn't, this attempts to explicitly cast it as a ``DataFrame``.

    :param data: The data to process.
    :type data: array-like, sequence, iterable, dict
    :raises InputError: Raised if the data cannot be converted to a
        ``DataFrame``, as required.
    :return: The data as a pandas ``DataFrame``.
    :rtype: :class:`pandas.DataFrame`
    """
    if isinstance(data, DataFrame):
        return clean_column_names(data)
    else:
        try:
            # Cast the data as a dataframe
            data = DataFrame(data)
        except Exception:
            raise InputError(
                f"Expected a pandas.Dataframe object, but got {type(data)}."
            )
        data = data.infer_objects()
    return clean_column_names(data)


def validate_univariate_input(data):
    """Ensures that *univariate input data* is of type :class:`pandas.Series`.

    If it isn't, this attempts to explicitly cast it as a ``Series``.

    :param data: The data to process.
    :type data: array-like, sequence, iterable, dict, scalar
    :raises InputError: Raised if the data cannot be converted to a
        ``Series``, as required.
    :return: The data as a pandas ``Series``.
    :rtype: :class:`pandas.Series`
    """
    if isinstance(data, Series):
        return data
    elif data is None or len(data) == 0:
        return Series([], dtype="object")
    else:
        try:
            # Cast the data as a series
            data = Series(data)
        except Exception:
            raise InputError(
                f"Expected a pandas.Series object, but got {type(data)}."
            )
    return data


def validate_target_variable(
    *, data: DataFrame, target_variable: Union[int, str]
) -> Union[Series, None]:
    """Ensures that the specified *target variable* (column label or index) is
    present in the data.

    Parameters
    ----------
    data : DataFrame
        The data being analysed.
    target_variable : Union[int, str]
        A column label or index.

    Returns
    -------
    union[Series, None]
        The target variable's data if ``target_variable`` is valid, or None.

    Raises
    ------
    InputError
        If the column label does not exist or the column index is out of
        bounds.
    """
    if target_variable is None:
        return None

    elif isinstance(target_variable, int):
        try:
            target_data = data.iloc[:, target_variable]
        except IndexError:
            raise InputError(
                f"Column index {target_variable} is not in the range"
                f" [0, {data.columns.size}]."
            )
        warn_if_target_data_has_high_cardinality(target_data)
        return target_data
    elif isinstance(target_variable, str):
        try:
            target_data = data[target_variable]
        except KeyError:
            raise InputError(
                f"{target_variable!r} is not in {data.columns.to_list()}"
            )
        warn_if_target_data_has_high_cardinality(target_data)
        return target_data
    else:
        # If target_variable is neither an index(int) or label(str)
        logging.warning(
            f"Target variable '{target_variable}' ignored."
            " Not a valid column index or label."
        )
        return None
