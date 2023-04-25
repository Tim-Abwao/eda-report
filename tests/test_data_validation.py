import pytest
from pandas import DataFrame, Series

from eda_report._validate import (
    _clean_column_labels,
    _validate_dataset,
    _validate_groupby_variable,
    _validate_univariate_input,
)
from eda_report.exceptions import (
    EmptyDataError,
    GroupbyVariableError,
    InputError,
)


class TestDatasetValidation:
    def test_dataframe_input(self):
        # Check if a dataframe is returned as a dataframe
        assert isinstance(_validate_dataset(DataFrame(range(10))), DataFrame)

    def test_series_input(self):
        # Check if a series returns a dataframe
        assert isinstance(_validate_dataset(Series(range(10))), DataFrame)

    def test_iterable_input(self):
        # Check if a sequence returns a dataframe
        assert isinstance(_validate_dataset(range(10)), DataFrame)
        # Check if a generator returns a dataframe
        assert isinstance(
            _validate_dataset((x**2 for x in range(10))), DataFrame
        )

    def test_invalid_input(self):
        # Check that invalid input rasies an InputError
        with pytest.raises(InputError) as error:
            _validate_dataset(0)
        assert (
            "Expected a pandas.Dataframe object, but got <class 'int'>."
            in str(error.value)
        )

    def test_empty_input(self):
        # Check that empty input rasies an EmptyDataError
        with pytest.raises(EmptyDataError) as error:
            _validate_dataset(DataFrame())
        assert "No data to process." in str(error.value)

    def test_empty_column_is_dropped(self):
        # Check that columns consisting entirely of NaN are dropped
        data_with_empty_col = [[x, None] for x in range(10)]
        result = _validate_dataset(data_with_empty_col)
        assert result.shape == (10, 1)


class TestUnivariateInputValidation:
    def test_series_input(self):
        # Check if a series is returned as a series
        assert isinstance(
            _validate_univariate_input(Series(range(10))), Series
        )

    def test_iterable_input(self):
        # Check if a sequence-like returns a series
        assert isinstance(_validate_univariate_input(range(10)), Series)
        # Check if a generator returns a series
        assert isinstance(
            _validate_univariate_input((x**2 for x in range(10))), Series
        )

    def test_empty_input(self):
        with pytest.raises(EmptyDataError) as error:
            _validate_univariate_input(x for x in [])
        assert "No data to process." in str(error.value)

    def test_null_input(self):
        assert _validate_univariate_input(None) is None

    def test_invalid_input(self):
        # Check that invalid input rasies an InputError
        with pytest.raises(InputError) as error:
            _validate_univariate_input(DataFrame([1, 2, 3]))
        assert (
            "Expected a one-dimensional sequence, but got "
            "<class 'pandas.core.frame.DataFrame'>."
        ) in str(error.value)


class TestTargetValidation:
    data = DataFrame([range(5)] * 3, columns=list("ABCDE"))

    def test_valid_column_index(self):
        # Check that a valid column index returns the appropriate column data.
        assert _validate_groupby_variable(
            data=self.data, groupby_variable=3
        ).equals(self.data.get("D"))

    def test_invalid_column_index(self):
        # Check that an error is raised for a column index that is out of
        # bounds.
        with pytest.raises(GroupbyVariableError) as error:
            _validate_groupby_variable(data=self.data, groupby_variable=10)
        assert "Column index 10 is not in the range [0, 5]." in str(
            error.value
        )

    def test_valid_column_label(self):
        # Check that a valid column label returns the appropriate column data.
        assert _validate_groupby_variable(
            data=self.data, groupby_variable="D"
        ).equals(self.data.get("D"))

    def test_invalid_column_label(self):
        # Check that an invalid column label raises an error.
        with pytest.raises(GroupbyVariableError) as error:
            _validate_groupby_variable(data=self.data, groupby_variable="X")
        assert "'X' is not in ['A', 'B', 'C', 'D', 'E']" in str(error.value)

    def test_null_input(self):
        # Check that `groupby_variable=None` returns `None`
        assert (
            _validate_groupby_variable(data=self.data, groupby_variable=None)
            is None
        )

    def test_invalid_input_type(self, caplog: pytest.LogCaptureFixture):
        # Check that invalid input (i.e not in {str, int, None} logs a warning
        # and returns None
        assert (
            _validate_groupby_variable(data=self.data, groupby_variable=1.0)
            is None
        )
        assert (
            "Group-by variable '1.0' ignored. "
            "Not a valid column index or label."
        ) in caplog.text

    def test_groupby_variable_with_excess_categories(
        self, caplog: pytest.LogCaptureFixture
    ):
        # Check that target variables with more than 10 unique values raise an
        # error and log a warning that color-coding won't be applied.
        _data = DataFrame([range(11)] * 2, index=["X", "Y"]).T
        expected_message = (
            "Group-by variable 'Y' not used to group values. "
            "It has high cardinality (11) and would clutter graphs."
        )
        with pytest.raises(GroupbyVariableError) as error:
            assert _validate_groupby_variable(
                data=_data, groupby_variable=1
            ).equals(_data.iloc[:, 1])
        assert expected_message in str(error.value)
        assert expected_message in caplog.text


class TestColumnLabelCleaning:
    def test_cleaning_rangeindex(self):
        with_rangeindex = DataFrame([[0, 1], [1, 2]])
        # Check if columns [0, 1] are changed to ["var_1", "var_2"]
        assert list(_clean_column_labels(with_rangeindex)) == [
            "var_1",
            "var_2",
        ]

    def test_cleaning_numeric_colnames(self):
        with_numeric_colnames = DataFrame([[1, 2], [3, 4]], columns=[1, 5])
        # Column names should be prefixed with "var_"
        assert list(_clean_column_labels(with_numeric_colnames)) == [
            "var_1",
            "var_5",
        ]

    def test_cleaning_mixed_colnames(self):
        with_mixed_colnames = DataFrame([[1, 2], [3, 4]], columns=[1, "B"])
        # Numeric column names should be converted to strings
        assert list(_clean_column_labels(with_mixed_colnames)) == ["1", "B"]
