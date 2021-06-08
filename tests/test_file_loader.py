import unittest
from pathlib import Path

import pandas as pd
from eda_report.exceptions import InputError
from eda_report.read_file import df_from_file


class TestFileLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create dummy data files
        cls.data = pd.DataFrame(range(50), columns=["data"])
        cls.data.to_excel("data.xlsx", index=False)
        cls.data.to_csv("data.csv", index=False)

    def test_csv_file_load(self):
        # Check that a valid csv file is read as a DataFrame
        self.assertTrue(df_from_file("data.csv").equals(self.data))

    def test_excel_file_load(self):
        # Check that a valid excel file is read as a DataFrame
        self.assertTrue(df_from_file("data.xlsx").equals(self.data))

    def test_invalid_file(self):
        # Check that an invalid file format/extension raises an InputError
        with self.assertRaises(InputError) as error:
            df_from_file("data.some_extension")
        # Check that the error message is as expected
        self.assertEqual(
            error.exception.message, "Invalid input file: data.some_extension"
        )

    @classmethod
    def tearDownClass(cls):
        for filename in {"data.csv", "data.xlsx"}:
            Path(filename).unlink()  # Delete the file
