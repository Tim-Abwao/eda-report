import logging

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


def validate_target_variable(*, data, target_variable):
    """Ensures that the supplied *target variable* (column label or index) is
    present in the data.

    :param target_variable: The column label or index of the target
        variable.
    :type target_variable: int, str, optional

    :raises InputError: Raised if a provided *column label* is *not in the
        data*, or a provided *column index* is *out of bounds*.

    :return: The name of the target variable, or None.
    :rtype: str, None
    """
    if target_variable is None:
        return None

    elif isinstance(target_variable, int):
        try:
            target_variable = data.columns[target_variable]
        except IndexError:
            raise InputError(
                f"Column index {target_variable} is not in the range"
                f" [0, {data.columns.size}]."
            )

    elif isinstance(target_variable, str):
        try:
            data.columns.get_loc(key=target_variable)
        except KeyError:
            raise InputError(
                f"{target_variable!r} is not in {data.columns.to_list()}"
            )

    else:
        # If target_variable is neither an index(int) or label(str)
        logging.warning(
            f"Target variable specifier '{target_variable}' ignored."
            " Not a valid column(feature) index or label."
        )
        return None

    if data[target_variable].nunique() > 10:
        logging.warning(
            f"Target variable '{target_variable}' not used to color-code "
            "graphs since it has too many levels "
            f"({data[target_variable].nunique()}) which would clutter graphs."
        )
    return target_variable
