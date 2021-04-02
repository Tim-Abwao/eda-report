from pandas import DataFrame, RangeIndex, Series

from eda_report.exceptions import InputError


def clean_column_names(data):
    """Makes sure that *columns/features* have *meaningful* names.

    If the input data has columns that are range-like (``RangeIndex`` e.g.
    [0, 1, 2, ...]), as is the case if an array/sequence/iterable is used to
    create a ``DataFrame`` but no column names are specified, then these
    columns will be renamed to ['var_1', 'var_2, ...]

    :param data: The data whose columns are checked
    :type data: ``pandas.DataFrame``
    """
    # Ensure the data has meaningful column names
    if isinstance(data.columns, RangeIndex):
        data.columns = [f'var_{i+1}' for i in data.columns]

    return data


def validate_multivariate_input(data):
    """Ensures that mutlivariate input data is of type ``pandas.DataFrame``.
    If it isn't, this attempts to explicitly cast it as a ``DataFrame``.

    :param data: The data to process.
    :type data: An array-like, sequence, iterable or dict
    :raises InputError: Raised if the data cannot be converted to a
        ``DataFrame``, as required.
    :return: The data as a pandas ``DataFrame``.
    :rtype: ``pandas.DataFrame``
    """
    if isinstance(data, DataFrame):
        return clean_column_names(data)
    else:
        try:
            # Cast the data as a dataframe
            data = DataFrame(data)
        except Exception:
            raise InputError(
                f'Expected a pandas.Dataframe object, but got {type(data)}.'
            )
        data = data.infer_objects()
    return clean_column_names(data)


def validate_univariate_input(data):
    """Ensures that univariate input data is of type ``pandas.Series``.
    If it isn't, this attempts to explicitly cast it as a ``Series``.

    :param data: The data to process.
    :type data: An array-like, sequence, iterable or dict
    :raises InputError: Raised if the data cannot be converted to a
        ``Series``, as required.
    :return: The data as a pandas ``Series``.
    :rtype: ``pandas.Series``
    """
    if isinstance(data, Series):
        return data
    else:
        try:
            # Cast the data as a series
            data = Series(data)
        except Exception:
            raise InputError(
                f'Expected a pandas.Series object, but got {type(data)}.'
            )
    return data
