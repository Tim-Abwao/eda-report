from pandas import DataFrame, RangeIndex
from eda_report.exceptions import InputError


def validate_input_dtype(data):
    """Check if the data is a pandas DataFrame, and raise an InputError if it
    isn't."""
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
