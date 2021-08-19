import pytest
from eda_report.exceptions import InputError
from eda_report.read_file import df_from_file
from pandas import DataFrame


class TestFileLoader:

    data = DataFrame(range(50), columns=["data"])

    def test_with_no_file_supplied(self):
        # Check that when no filepath is specified, None is returned.
        assert df_from_file() is None

    def test_csv_file_load(self, tmp_path):
        # Check that a valid csv file is read as a DataFrame
        csv_file = tmp_path / "data.csv"
        self.data.to_csv(csv_file, index=False)
        assert df_from_file(csv_file).equals(self.data)

    def test_excel_file_load(self, tmp_path):
        # Check that a valid excel file is read as a DataFrame
        excel_file = tmp_path / "data.xlsx"
        self.data.to_excel(excel_file, index=False)
        assert df_from_file(excel_file).equals(self.data) is True

    def test_invalid_file(self):
        # Check that an invalid file format/extension raises an InputError
        with pytest.raises(InputError) as error:
            df_from_file("data.some_extension")
        # Check that the error message is as expected
        assert "Invalid input file: data.some_extension" in str(error.value)
