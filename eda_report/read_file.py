import pandas as pd
from eda_report.exceptions import InputError


def df_from_file(filename):
    """Load the file `filename` as a pandas DataFrame."""
    file_extension = filename.rsplit('.')[-1]

    if file_extension == 'csv':
        return pd.read_csv(filename)
    elif file_extension == 'xlsx':
        return pd.read_excel(filename, engine='openpyxl')
    else:
        raise InputError(f'Invalid input file: {filename}')
