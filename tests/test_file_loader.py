import pytest
from pandas import DataFrame

from eda_report.exceptions import InputError
from eda_report.read_file import df_from_file


class TestFileLoader:
    data = DataFrame([[1, 2, 3], [4, 5, 6]], columns=list("ABC"))

    def test_csv_file_load(self, temp_data_dir):
        # Check that a valid csv file is read as a DataFrame
        assert df_from_file(temp_data_dir / "data.csv").equals(self.data)

    def test_excel_file_load(self, temp_data_dir):
        # Check that a valid excel file is read as a DataFrame
        assert df_from_file(temp_data_dir / "data.xlsx").equals(self.data)

    def test_invalid_file(self):
        # Check that an invalid file format/extension raises an InputError
        with pytest.raises(InputError) as error:
            df_from_file("data.some_extension")
        # Check that the error message is as expected
        assert "Invalid input file: 'data.some_extension'" in str(error.value)
