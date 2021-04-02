import unittest

import pandas as pd
from eda_report.exceptions import InputError
from eda_report.validate import (clean_column_names,
                                 validate_multivariate_input,
                                 validate_univariate_input)


class TestDataValidation(unittest.TestCase):

    def setUp(self):
        self.dataframe = pd.DataFrame(range(50))
        self.series = self.dataframe.squeeze()

    def test_multivariate_input_validation(self):
        # Check if a dataframe is returned as a dataframe
        self.assertIsInstance(
            validate_multivariate_input(self.dataframe), pd.DataFrame
        )
        # Check if a series returns a dataframe
        self.assertIsInstance(
            validate_multivariate_input(self.series), pd.DataFrame
        )
        # Check if a sequence-like returns a dataframe
        self.assertIsInstance(
            validate_multivariate_input(range(50)), pd.DataFrame
        )
        # Check that invalid input rasies an InputError
        self.assertRaises(
            InputError, validate_multivariate_input, 0
        )

    def test_univariate_input_validation(self):
        # Check if a series is returned as a series
        self.assertIsInstance(
            validate_univariate_input(self.series), pd.Series
        )
        # Check if a sequence-like returns a series
        self.assertIsInstance(
            validate_univariate_input(range(50)), pd.Series
        )
        # Check that invalid input rasies an InputError
        self.assertRaises(
            InputError, validate_univariate_input, pd.DataFrame(range(10))
        )

    def test_column_cleaning(self):
        self.assertEqual(
            clean_column_names(self.dataframe).columns.to_list(),
            ['var_1']
        )
