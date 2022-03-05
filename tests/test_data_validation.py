import pytest
from eda_report.exceptions import (
    EmptyDataError,
    InputError,
    TargetVariableError,
)
from eda_report.validate import (
    clean_column_labels,
    validate_multivariate_input,
    validate_target_variable,
    validate_univariate_input,
)
from pandas import DataFrame, Series


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

    def test_empty_input(self):
        # Check that empty input rasies an EmptyDataError
        with pytest.raises(EmptyDataError) as error:
            validate_multivariate_input(DataFrame())
        assert "No data to process." in str(error.value)


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

    def test_empty_input(self):
        with pytest.raises(EmptyDataError) as error:
            validate_univariate_input(x for x in [])
        assert "No data to process." in str(error.value)

    def test_null_input(self):
        assert validate_univariate_input(None) is None

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
        # Check that a valid column index returns the appropriate column data.
        assert validate_target_variable(
            data=self.data, target_variable=3
        ).equals(self.data.get("D"))

    def test_invalid_column_index(self):
        # Check that an input error is raised for a column index that is out
        # of bounds.
        with pytest.raises(TargetVariableError) as error:
            validate_target_variable(data=self.data, target_variable=10)
        assert "Column index 10 is not in the range [0, 5]." in str(
            error.value
        )

    def test_valid_column_label(self):
        # Check that a valid column label returns the appropriate column data.
        assert validate_target_variable(
            data=self.data, target_variable="D"
        ).equals(self.data.get("D"))

    def test_invalid_column_label(self):
        # Check that an invalid column label raises an input error.
        with pytest.raises(TargetVariableError) as error:
            validate_target_variable(data=self.data, target_variable="X")
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
        # Check that target variables with more than 10 unique values raise an
        # error and log a warning that color-coding won't be applied.
        _data = DataFrame([range(11)] * 2, index=["X", "Y"]).T
        expected_message = (
            "Target variable 'Y' not used to group values. "
            "It has high cardinality (11) and would clutter graphs."
        )
        with pytest.raises(TargetVariableError) as error:
            assert validate_target_variable(
                data=_data, target_variable=1
            ).equals(_data.iloc[:, 1])
        assert expected_message in str(error.value)
        assert expected_message in caplog.text


def test_column_cleaning():
    df1 = DataFrame([[0, 1], [1, 2]])
    df2 = DataFrame([[1, 2], [3, 4]], columns=[1, 2])
    # Check if columns [0, 1, ...] are changed to ["var_1", "var_2", ...]
    assert clean_column_labels(df1).columns.to_list() == ["var_1", "var_2"]
    assert clean_column_labels(df2).columns.to_list() == ["var_1", "var_2"]
