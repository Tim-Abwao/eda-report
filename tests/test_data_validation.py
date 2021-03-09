import pandas as pd
import unittest
from eda_report.validate import validate_input_dtype, clean_column_names


class TestDataValidation(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame(range(50))

    def test_data_type_validation(self):
        # Check if a dataframe is returned as a dataframe
        self.assertIsInstance(
            validate_input_dtype(self.data), pd.DataFrame
        )
        # Check if a series returns a dataframe
        self.assertIsInstance(
            validate_input_dtype(self.data.squeeze()), pd.DataFrame
        )
        # Check if a sequence returns a dataframe
        self.assertIsInstance(
            validate_input_dtype(range(50)), pd.DataFrame
        )

    def test_column_cleaning(self):
        self.assertEqual(
            clean_column_names(self.data).columns.to_list(),
            ['var_1']
        )
