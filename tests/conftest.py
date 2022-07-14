from shutil import rmtree

import pytest
from pandas import DataFrame


@pytest.fixture(scope="session")
def temp_data_dir(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("data")
    sample_data = DataFrame([[1, 2, 3], [4, 5, 6]], columns=list("ABC"))
    sample_data.to_csv(temp_dir / "data.csv", index=False)
    sample_data.to_excel(temp_dir / "data.xlsx", index=False)
    yield temp_dir
    rmtree(temp_dir)
