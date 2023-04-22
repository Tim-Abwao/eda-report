import pytest
from pandas import DataFrame, Series

from eda_report.exceptions import (
    EmptyDataError,
    GroupbyVariableError,
    InputError,
)
from eda_report.validate import (
    clean_column_labels,
    validate_groupby_data,
    validate_multivariate_input,
    validate_univariate_input,
)


class TestMultivariateInputValidation:
    def test_dataframe_input(self):
        # Check if a dataframe is returned as a dataframe
        assert isinstance(
            validate_multivariate_input(DataFrame(range(10))), DataFrame
        )

    def test_series_input(self):
        # Check if a series returns a dataframe
        assert isinstance(
            validate_multivariate_input(Series(range(10))), DataFrame
        )

    def test_iterable_input(self):
        # Check if a sequence returns a dataframe
        assert isinstance(validate_multivariate_input(range(10)), DataFrame)
        # Check if a generator returns a dataframe
        assert isinstance(
            validate_multivariate_input((x**2 for x in range(10))), DataFrame
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

    def test_empty_column_is_dropped(self):
        # Check that columns consisting entirely of NaN are dropped
        data_with_empty_col = [[x, None] for x in range(10)]
        result = validate_multivariate_input(data_with_empty_col)
        assert result.shape == (10, 1)


class TestUnivariateInputValidation:
    def test_series_input(self):
        # Check if a series is returned as a series
        assert isinstance(validate_univariate_input(Series(range(10))), Series)

    def test_iterable_input(self):
        # Check if a sequence-like returns a series
        assert isinstance(validate_univariate_input(range(10)), Series)
        # Check if a generator returns a series
        assert isinstance(
            validate_univariate_input((x**2 for x in range(10))), Series
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
        assert validate_groupby_data(data=self.data, groupby_data=3).equals(
            self.data.get("D")
        )

    def test_invalid_column_index(self):
        # Check that an error is raised for a column index that is out of
        # bounds.
        with pytest.raises(GroupbyVariableError) as error:
            validate_groupby_data(data=self.data, groupby_data=10)
        assert "Column index 10 is not in the range [0, 5]." in str(
            error.value
        )

    def test_valid_column_label(self):
        # Check that a valid column label returns the appropriate column data.
        assert validate_groupby_data(data=self.data, groupby_data="D").equals(
            self.data.get("D")
        )

    def test_invalid_column_label(self):
        # Check that an invalid column label raises an error.
        with pytest.raises(GroupbyVariableError) as error:
            validate_groupby_data(data=self.data, groupby_data="X")
        assert "'X' is not in ['A', 'B', 'C', 'D', 'E']" in str(error.value)

    def test_null_input(self):
        # Check that `groupby_data=None` returns `None`
        assert validate_groupby_data(data=self.data, groupby_data=None) is None

    def test_invalid_input_type(self, caplog):
        # Check that invalid input (i.e not in {str, int, None} logs a warning
        # and returns None
        assert validate_groupby_data(data=self.data, groupby_data=1.0) is None
        assert (
            "Group-by variable '1.0' ignored. "
            "Not a valid column index or label."
        ) in caplog.text

    def test_groupby_data_with_excess_categories(self, caplog):
        # Check that target variables with more than 10 unique values raise an
        # error and log a warning that color-coding won't be applied.
        _data = DataFrame([range(11)] * 2, index=["X", "Y"]).T
        expected_message = (
            "Group-by variable 'Y' not used to group values. "
            "It has high cardinality (11) and would clutter graphs."
        )
        with pytest.raises(GroupbyVariableError) as error:
            assert validate_groupby_data(data=_data, groupby_data=1).equals(
                _data.iloc[:, 1]
            )
        assert expected_message in str(error.value)
        assert expected_message in caplog.text


class TestColumnLabelCleaning:
    def test_cleaning_rangeindex(self):
        with_rangeindex = DataFrame([[0, 1], [1, 2]])
        # Check if columns [0, 1] are changed to ["var_1", "var_2"]
        assert list(clean_column_labels(with_rangeindex)) == ["var_1", "var_2"]

    def test_cleaning_numeric_colnames(self):
        with_numeric_colnames = DataFrame([[1, 2], [3, 4]], columns=[1, 5])
        # Column names should be prefixed with "var_"
        assert list(clean_column_labels(with_numeric_colnames)) == [
            "var_1",
            "var_5",
        ]

    def test_cleaning_mixed_colnames(self):
        with_mixed_colnames = DataFrame([[1, 2], [3, 4]], columns=[1, "B"])
        # Numeric column names should be converted to strings
        assert list(clean_column_labels(with_mixed_colnames)) == ["1", "B"]
