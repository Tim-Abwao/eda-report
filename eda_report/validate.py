from pandas import DataFrame, RangeIndex
from eda_report.exceptions import InputError


def validate_input_dtype(data):
    """Ensures that the data is of type ``pandas.DataFrame``. If it isn't,
    attempt to explicitly cast it as a ``DataFrame``.

    :param data: The data to process.
    :type data: An array-like, sequence, iterable or dict
    :raises InputError: Raised if the data cannot be converted to a
        ``DataFrame``, as required.
    :return: The data as a pandas ``DataFrame``.
    :rtype: ``pandas.DataFrame``
    """
    if isinstance(data, DataFrame):
        return data
    else:
        try:
            # Cast the data as a dataframe
            data = DataFrame(data).infer_objects()
            # Ensure the data has meaningful column names
            if isinstance(data.columns, RangeIndex):
                data.columns = [f'var_{i+1}' for i in data.columns]
            return data
        except Exception:
            raise InputError(
                f'Expected a pandas.Dataframe object, but got {type(data)}.'
            )
