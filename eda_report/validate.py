import logging
from collections.abc import Iterable
from typing import Optional, Union
from types import GeneratorType

from pandas import DataFrame, RangeIndex, Series
from pandas.api.types import is_numeric_dtype

from eda_report.exceptions import (
    EmptyDataError,
    InputError,
    TargetVariableError,
)


def clean_column_labels(data: DataFrame) -> DataFrame:
    """Makes sure that *columns* have *meaningful* names.

    When an ``Iterable`` is used to create a ``DataFrame`` and no column names
    are provided, the column labels by default are set as a
    :class:`~pandas.RangeIndex` — [0, 1, 2, ...].

    This function renames such columns to ['var_1', 'var_2, 'var_3', ...],
    making references and comparisons much more intuitive. It also ensures
    that column labels are of type ``str`` to allow sorting and the use of
    string methods.

    Parameters
    ----------
    data : DataFrame
        Data to inspect and perhaps edit.

    Returns
    -------
    DataFrame
        The data, with reader-friendly column names.
    """
    # Prepend "var_" to entirely numeric column labels
    if isinstance(data.columns, RangeIndex) or is_numeric_dtype(data.columns):
        data.columns = [f"var_{i+1}" for i in data.columns]
        return data

    # Ensure all column labels are of type str to allow sorting, and so that
    # string methods can be used.
    data.columns = [str(col) for col in data.columns]
    return data


def check_cardinality(target_data: Series, threshold: int = 10) -> None:
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
        message = (
            f"Target variable '{target_data.name}' not used to group values. "
            f"It has high cardinality ({target_data.nunique()}) "
            f"and would clutter graphs."
        )
        logging.warning(message)
        raise TargetVariableError(message)


def validate_multivariate_input(data: Iterable) -> DataFrame:
    """Ensures that *multivariate input data* is of type :class:`pandas.DataFrame`.

    If it isn't, this attempts to explicitly cast it as a ``DataFrame``.

    Parameters
    ----------
    data : Iterable
        The data to analyse.

    Returns
    -------
    DataFrame
        The input data as a ``DataFrame``.

    Raises
    ------
    InputError
        If the ``data`` cannot be cast as a :class:`~pandas.DataFrame`.
    EmptyDataError
        If the ``data`` has no rows (has length zero).
    """
    if isinstance(data, DataFrame):
        data_frame = data
    else:
        try:
            data_frame = DataFrame(data)
        except Exception:
            raise InputError(
                f"Expected a pandas.Dataframe object, but got {type(data)}."
            )
        # Attempt to infer better dtypes for object columns.
        data_frame = data_frame.infer_objects()

    # The data should not be empty
    if len(data_frame) == 0:
        raise EmptyDataError("The supplied data has length zero.")

    return clean_column_labels(data_frame)


def validate_univariate_input(
    data: Iterable, *, name: Optional[str] = None
) -> Series:
    """Ensures that *univariate input data* is of type :class:`pandas.Series`.

    If it isn't, this attempts to explicitly cast it as a ``Series``.

    Parameters
    ----------
    data : Iterable
        The data to analyse.
    name : Optional[str]
        The name to assign the data, by default None.

    Returns
    -------
    Series
        The input data as a ``Series``.

    Raises
    ------
    InputError
        If the ``data`` cannot be cast as a :class:`~pandas.Series`.
    """
    if isinstance(data, GeneratorType):
        return Series(data, name=name)

    elif issubclass(type(data), Iterable) and len(list(data)) > 0:

        if isinstance(data, Series):
            name_ = name or data.name
            return data.rename(name_)

        else:
            try:
                data = Series(data, name=name)
            except Exception:
                raise InputError(
                    f"Expected a one-dimensional sequence, "
                    f"but got {type(data)}."
                )
            else:
                return data
    else:
        raise InputError("No data to process.")


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
    TargetVariableError
        If the supplied column label does not exist, or the supplied column
        index is out of bounds.
    """
    if target_variable is None:
        return None

    elif isinstance(target_variable, int):
        try:
            target_data = data.iloc[:, target_variable]
        except IndexError:
            raise TargetVariableError(
                f"Column index {target_variable} is not in the range"
                f" [0, {data.columns.size}]."
            )
        check_cardinality(target_data)
        return target_data
    elif isinstance(target_variable, str):
        try:
            target_data = data[target_variable]
        except KeyError:
            raise TargetVariableError(
                f"{target_variable!r} is not in {data.columns.to_list()}"
            )
        check_cardinality(target_data)
        return target_data
    else:
        # If target_variable is neither an index(int) or label(str)
        logging.warning(
            f"Target variable '{target_variable}' ignored."
            " Not a valid column index or label."
        )
        return None
