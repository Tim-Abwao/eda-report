import pytest

from pandas import DataFrame, Series
from eda_report.exceptions import InputError
from eda_report.validate import (
    clean_column_names,
    validate_multivariate_input,
    validate_target_variable,
    validate_univariate_input,
)


class TestMultivariateInputValidation:

    data = range(10)

    def test_dataframe_input(self):
        # Check if a dataframe is returned as a dataframe
        assert isinstance(
            validate_multivariate_input(DataFrame(self.data)), DataFrame
        )

    def test_series_input(self):
        # Check if a series returns a dataframe
        assert isinstance(
            validate_multivariate_input(Series(self.data)), DataFrame
        )

    def test_iterable_input(self):
        # Check if a sequence returns a dataframe
        assert isinstance(validate_multivariate_input(self.data), DataFrame)
        # Check if a generator returns a dataframe
        assert isinstance(
            validate_multivariate_input((x ** 2 for x in self.data)), DataFrame
        )

    def test_invalid_input(self):
        # Check that invalid input rasies an InputError
        with pytest.raises(InputError) as error:
            validate_multivariate_input(0)
        assert (
            "Expected a pandas.Dataframe object, but got <class 'int'>."
            in str(error.value)
        )


class TestUnivariateInputValidation:

    data = range(10)

    def test_series_input(self):
        # Check if a series is returned as a series
        assert isinstance(validate_univariate_input(Series(self.data)), Series)

    def test_iterable_input(self):
        # Check if a sequence-like returns a series
        assert isinstance(validate_univariate_input(self.data), Series)
        # Check if a generator returns a series
        assert isinstance(
            validate_univariate_input((x ** 2 for x in self.data)), Series
        )

    def test_null_input(self):
        with pytest.raises(InputError) as error:
            validate_univariate_input(None)
        assert "No data to process." in str(error.value)

    def test_invalid_input(self):
        # Check that invalid input rasies an InputError
        with pytest.raises(InputError) as error:
            validate_univariate_input(DataFrame([1, 2, 3]))
        assert (
            "Expected a one-dimensional sequence, but got "
            "<class 'pandas.core.frame.DataFrame'>."
        ) in str(error.value)


class TestTargetValidation:

    data = DataFrame([range(5)] * 3, columns=list("ABCDE"))

    def test_valid_column_index(self):
        # Check that a valid column index returns the appropriate column label.
        # In this case, check that the column at index 3 is "D".
        assert validate_target_variable(
            data=self.data, target_variable=3
        ).equals(self.data.get("D"))

    def test_invalid_column_index(self):
        # Check that an input error is raised for a column index that is out
        # of bounds.
        with pytest.raises(InputError) as error:
            validate_target_variable(data=self.data, target_variable=10)
        # Check that the error message is as expected
        assert "Column index 10 is not in the range [0, 5]." in str(
            error.value
        )

    def test_valid_column_label(self):
        # Check that a valid column label is returned.
        # In this case, check that column "D" is present (returned).
        assert validate_target_variable(
            data=self.data, target_variable="D"
        ).equals(self.data.get("D"))

    def test_invalid_column_label(self):
        # Check that an invalid column label raises an input error.
        # In this case, check that "X" is not a column in the data.
        with pytest.raises(InputError) as error:
            validate_target_variable(data=self.data, target_variable="X")
        # Check that the error message is as expected
        assert "'X' is not in ['A', 'B', 'C', 'D', 'E']" in str(error.value)

    def test_null_input(self):
        # Check that `target_data=None` returns `None`
        assert (
            validate_target_variable(data=self.data, target_variable=None)
            is None
        )

    def test_invalid_input_type(self, caplog):
        # Check that invalid input (i.e not in {str, int, None} logs a warning
        # and returns None
        assert (
            validate_target_variable(data=self.data, target_variable=1.0)
            is None
        )
        assert (
            "Target variable '1.0' ignored. Not a valid column index or label."
        ) in caplog.text

    def test_target_variable_with_excess_categories(self, caplog):
        # Check that target variables with more than 10 unique values log a
        # warning that color-coding won't be applied.
        _data = DataFrame([range(11)] * 2).T
        assert validate_target_variable(data=_data, target_variable=1).equals(
            _data.iloc[:, 1]
        )
        # Check that the warning message is as expected
        assert (
            "Target variable '1' not used to color-code graphs since it has "
            "high cardinality (11) which would clutter graphs."
        ) in caplog.text


def test_column_cleaning():
    dataframe = DataFrame([[0, 1], [1, 2]])
    # Check if columns [0, 1, ...] are changed to ["var_1", "var_2", ...]
    assert clean_column_names(dataframe).columns.to_list() == [
        "var_1",
        "var_2",
    ]
