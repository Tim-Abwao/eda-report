import logging
from collections.abc import Iterable
from typing import Optional, Union

from pandas import DataFrame, RangeIndex, Series
from pandas.api.types import is_numeric_dtype

from eda_report.exceptions import (
    EmptyDataError,
    GroupbyVariableError,
    InputError,
)


def clean_column_labels(data: DataFrame) -> DataFrame:
    """Makes sure that columns have *meaningful* names.

    When creating a ``DataFrame`` from an ``Iterable``, if no column names
    are provided, the columns are set as a :class:`~pandas.RangeIndex` —
    [0, 1, 2, ...] (default).

    This function renames such columns to ['var_1', 'var_2, 'var_3', ...],
    making references and comparisons much more intuitive.

    It also ensures that column labels are all of similar type (``str``) to
    allow sorting and the use of string methods.

    Args:
        data (pandas.DataFrame): Data to inspect and perhaps edit.

    Returns:
        pandas.DataFrame: The ``data``, with reader-friendly column
        names.
    """
    if isinstance(data.columns, RangeIndex):
        data.columns = [f"var_{i+1}" for i in data.columns]
    elif is_numeric_dtype(data.columns):
        data.columns = [f"var_{i}" for i in data.columns]
        return data
    else:
        data.columns = data.columns.map(str)
    return data


def check_cardinality(groupby_data: Series, *, threshold: int = 10) -> None:
    """Assesses whether the ``groupby_data`` has too many unique values
    (> ``threshold``, default 10).

    Args:
        groupby_data (pandas.Series): The data intended to group values.
        threshold (int, optional): Maximum allowable cardinality. Defaults to
            10.

    Raises:
        GroupbyVariableError: If the `groupby_data` has cardinality outside the
            acceptable range.
    """
    if groupby_data.nunique() > threshold:
        message = (
            f"Group-by variable '{groupby_data.name}' not used to group "
            f"values. It has high cardinality ({groupby_data.nunique()}) "
            f"and would clutter graphs."
        )
        logging.warning(message)
        raise GroupbyVariableError(message)


def validate_multivariate_input(data: Iterable) -> DataFrame:
    """Ensures that *multivariate input data* is of type
    :class:`pandas.DataFrame`.

    If it isn't, this attempts to explicitly cast it as a ``DataFrame``.

    Columns in the data that are completely empty will be dropped.

    Args:
        data (Iterable): The data to analyze.

    Raises:
        InputError: If the ``data`` cannot be cast as a
            :class:`~pandas.DataFrame`.
        EmptyDataError: If the ``data`` has no items.

    Returns:
        pandas.DataFrame: The input data as a DataFrame.
    """
    try:
        data_frame = DataFrame(data)
    except Exception:
        raise InputError(
            f"Expected a pandas.Dataframe object, but got {type(data)}."
        )
    # The data should not be empty
    if len(data_frame) == 0:
        raise EmptyDataError("No data to process.")

    data_frame = (
        # Attempt to infer better dtypes for columns.
        data_frame.infer_objects()
        # Drop completely empty columns.
        .dropna(axis=1, how="all")
    )
    return clean_column_labels(data_frame)


def validate_univariate_input(
    data: Iterable, *, name: str = None
) -> Optional[Series]:
    """Ensures that *univariate input data* is of type :class:`pandas.Series`.

    If it isn't, this attempts to explicitly cast it as a ``Series``.

    Args:
        data (Iterable): The data to analyze.
        name (str, optional): The name to assign the data. Defaults
            to None.

    Raises:
        InputError: If the ``data`` cannot be cast as a
            :class:`~pandas.Series`.
        EmptyDataError: If the ``data`` has no items.

    Returns:
        Optional[pandas.Series]: The input data as a ``Series``.
    """
    if data is None:
        return None
    else:
        try:
            series = Series(data, name=name)
        except Exception:
            raise InputError(
                f"Expected a one-dimensional sequence, but got {type(data)}."
            )
    if series.shape[0] == 0:
        raise EmptyDataError("No data to process.")
    else:
        return series


def validate_groupby_data(
    *, data: DataFrame, groupby_data: Union[int, str]
) -> Optional[Series]:
    """Ensures that the specified column label/index for grouping values is
    present in the data.

    Args:
        data (DataFrame): The data being analyzed.
        groupby_data (Union[int, str]): A column label or index.

    Raises:
        GroupbyVariableError: If the supplied column label does not exist, or
            the supplied column index is out of bounds.

    Returns:
        Optional[pandas.Series]: The groupby variable's data.
    """
    if groupby_data is None:
        return None
    elif f"{groupby_data}".isdecimal():
        idx = int(groupby_data)
        try:
            groupby_data = data.iloc[:, idx]
        except IndexError:
            raise GroupbyVariableError(
                f"Column index {groupby_data} is not in the range"
                f" [0, {data.columns.size}]."
            )
        check_cardinality(groupby_data)
        return groupby_data
    elif isinstance(groupby_data, str):
        try:
            groupby_data = data[groupby_data]
        except KeyError:
            raise GroupbyVariableError(
                f"{groupby_data!r} is not in {data.columns.to_list()}"
            )
        check_cardinality(groupby_data)
        return groupby_data
    else:
        # If groupby_data is neither an index(int) or label(str)
        logging.warning(
            f"Group-by variable '{groupby_data}' ignored."
            " Not a valid column index or label."
        )
        return None
