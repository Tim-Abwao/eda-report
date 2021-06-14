import unittest

import pandas as pd
from eda_report.exceptions import InputError
from eda_report.validate import (
    clean_column_names,
    validate_multivariate_input,
    validate_target_variable,
    validate_univariate_input,
)


class TestDataValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create dummy data
        cls.dataframe = pd.DataFrame(range(50))
        cls.series = cls.dataframe.squeeze()

    @classmethod
    def tearDownClass(cls):
        del cls.dataframe, cls.series

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
        self.assertRaises(InputError, validate_multivariate_input, 0)

    def test_univariate_input_validation(self):
        # Check if a series is returned as a series
        self.assertIsInstance(
            validate_univariate_input(self.series), pd.Series
        )
        # Check if a sequence-like returns a series
        self.assertIsInstance(validate_univariate_input(range(50)), pd.Series)
        # Check that invalid input rasies an InputError
        self.assertRaises(
            InputError, validate_univariate_input, pd.DataFrame(range(10))
        )

    def test_column_cleaning(self):
        # Check if columns [0, 1, ...] are changed to ["var_1", "var_2", ...]
        self.assertEqual(
            clean_column_names(self.dataframe).columns.to_list(), ["var_1"]
        )


class TestTargetValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create dummy data
        cls.data = pd.DataFrame([range(5)] * 3, columns=list("ABCDE"))

    @classmethod
    def tearDownClass(cls):
        del cls.data

    def test_valid_column_index(self):
        # Check that a valid column index returns the appropriate column label.
        # In this case, check that the column at index 3 is "D".
        self.assertEqual(
            validate_target_variable(data=self.data, target_variable=3), "D"
        )

    def test_invalid_column_index(self):
        # Check that an input error is raised for a column index that is out
        # of bounds.
        with self.assertRaises(InputError) as error:
            validate_target_variable(data=self.data, target_variable=10)
        # Check that the error message is as expected
        self.assertEqual(
            error.exception.message,
            "Column index 10 is not in the range [0, 5].",
        )

    def test_valid_column_label(self):
        # Check that a valid column label is returned.
        # In this case, check that column "D" is present (returned).
        self.assertEqual(
            validate_target_variable(data=self.data, target_variable="D"), "D"
        )

    def test_invalid_column_label(self):
        # Check that an invalid column label raises an input error.
        # In this case, check that "X" is not a column in the data.
        with self.assertRaises(InputError) as error:
            validate_target_variable(data=self.data, target_variable="X")
        # Check that the error message is as expected
        self.assertEqual(
            error.exception.message,
            "'X' is not in ['A', 'B', 'C', 'D', 'E']",
        )

    def test_null_input(self):
        # Check that `target_data=None` returns `None`
        self.assertIsNone(
            validate_target_variable(data=self.data, target_variable=None)
        )

    def test_invalid_input_type(self):
        # Check that invalid input (i.e not in {str, int, None} logs a warning
        with self.assertLogs(level="WARNING") as logged_warning:
            # Check that invalid input type returns None
            self.assertIsNone(
                validate_target_variable(data=self.data, target_variable=1.0)
            )
            # Check that the warning message is as expected
            self.assertEqual(
                logged_warning.records[-1].message,
                "Target variable specifier '1.0' ignored. Not a valid "
                "column(feature) index or label.",
            )

    def test_target_variable_with_excess_categories(self):
        # Check that target variables with more than 10 unique values log a
        # warning that color-coding won't be applied.
        with self.assertLogs(level="WARNING") as logged_warning:
            _data = pd.DataFrame([range(11)] * 2).T
            validate_target_variable(data=_data, target_variable=1)
            # Check that the warning message is as expected
            self.assertEqual(
                logged_warning.records[-1].message,
                "Target variable '1' not used to color-code graphs since it "
                "has too many levels (11) which would clutter graphs.",
            )
