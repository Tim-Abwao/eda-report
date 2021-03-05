import pandas as pd
import os
import unittest
from eda_report.exceptions import InputError
from eda_report.read_file import df_from_file


class TestFileLoader(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame(range(50), columns=['data'])  # sample data

        # Save the sample data as the files
        self.data.to_excel('data.xlsx', index=False)
        self.data.to_csv('data.csv', index=False)

    def test_csv_file_load(self):
        self.assertTrue(df_from_file('data.csv').equals(self.data))

    def test_excel_file_load(self):
        self.assertTrue(df_from_file('data.xlsx').equals(self.data))

    def test_invalid_file(self):
        self.assertRaises(InputError, df_from_file, 'data.some_extension')

    def tearDown(self):
        for file in {'data.csv', 'data.xlsx'}:
            if os.path.isfile(file):
                os.remove(file)
