import pandas as pd
from pathlib import Path
from eda_report.exceptions import InputError


def df_from_file(filename):
    """Read a csv or excel file and load its contents as a
    ``pandas.DataFrame``.

    :param filename: A file name, or the path to a file.
    :type filename: str
    :raises InputError: If the input file is not a valid csv or excel file.
    :return: A pandas ``DataFrame``.
    :rtype: ``pandas.DataFrame``
    """
    file = Path(filename)

    if file.suffix == '.csv':
        return pd.read_csv(file)
    elif file.suffix == '.xlsx':
        return pd.read_excel(file, engine='openpyxl')
    else:
        raise InputError(f'Invalid input file: {filename}')
