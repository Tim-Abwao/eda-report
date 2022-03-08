from pathlib import Path
from typing import Union

import pandas as pd

from eda_report.exceptions import InputError


def df_from_file(filepath: Union[str, Path]) -> pd.DataFrame:
    """Reads a file, and loads its contents as a :class:`~pandas.DataFrame`.

    File formats are currently restricted to *csv* and *excel*, since these
    are the most often used to store data.

    This is basically a wrapper around ``pandas'`` input functions:

        * :func:`pandas.read_csv`
        * :func:`pandas.read_excel`


    Args:
        filepath (Union[str, Path]): The path to a file.

    Raises:
        InputError: If the supplied filepath is invalid, for instance if the
            file is of an incorrect format or does not exist.

    Returns:
        pandas.core.frame.DataFrame: The specified file's contents.
    """
    file = Path(filepath)

    if file.suffix == ".csv":
        return pd.read_csv(file)
    elif file.suffix == ".xlsx":
        return pd.read_excel(file, engine="openpyxl")
    else:
        raise InputError(f"Invalid input file: {filepath}")
