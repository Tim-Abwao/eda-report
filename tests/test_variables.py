import pytest
from eda_report.univariate import (
    CategoricalVariable,
    DatetimeVariable,
    NumericVariable,
    Variable,
)
from pandas import Series, Timestamp, date_range
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


def test_dtype_detection():
    assert Variable([True, False]).var_type == "boolean"
    assert Variable([0, 1, 1, 0, 1]).var_type == "boolean"
    assert Variable(list("abcdefg")).var_type == "categorical"
    assert Variable([1, 2, 3] * 10).var_type == "categorical"
    assert (
        Variable(date_range("2022-01-01", periods=5, freq="D")).var_type
        == "datetime"
    )
    assert Variable(range(15)).var_type == "numeric"


class TestGeneralVariable:

    variable = Variable([1, 2, 3, 5, 8, None], name="some-variable")
    unnamed_variable = Variable(list("ababdea"))

    def test_data_type(self):
        assert isinstance(self.variable.data, Series)
        assert isinstance(self.unnamed_variable.data, Series)
        assert is_numeric_dtype(self.variable.data)
        assert is_object_dtype(self.unnamed_variable.data)
        assert self.variable.var_type == "numeric"
        assert self.unnamed_variable.var_type == "categorical"

    def test_missing_values(self):
        assert self.variable.missing == "1 (16.67%)"
        assert self.unnamed_variable.missing is None

    def test_name(self):
        assert self.variable.name == "some-variable"
        assert self.unnamed_variable.name is None

    def test_renaming(self):
        self.variable.rename("new name")
        assert self.variable.name == "new name"

        self.variable.rename()
        assert self.variable.name is None

    def test_unique_values(self):
        assert self.variable.num_unique == 5
        assert self.variable.unique == pytest.approx([1.0, 2.0, 3.0, 5.0, 8.0])

        assert self.unnamed_variable.num_unique == 4
        assert self.unnamed_variable.unique == list("abde")


class TestCategoricalVariables:

    majority_unique = CategoricalVariable(["a", "b", "c", "d", None, "a"])
    majority_repeating = CategoricalVariable(["a", "b", "c", "d"] * 3)

    def test_data_type(self):
        assert is_object_dtype(self.majority_unique.data)
        assert self.majority_unique.var_type == "categorical"

        assert is_categorical_dtype(self.majority_repeating.data)
        assert self.majority_repeating.var_type == "categorical"

    def test_summary_statistics(self):
        assert self.majority_unique._get_most_common().to_dict() == {
            "a": "2 (33.33%)",
            "b": "1 (16.67%)",
            "c": "1 (16.67%)",
            "d": "1 (16.67%)",
        }
        assert self.majority_unique._get_summary_statistics().to_dict() == {
            "Number of observations": 5,
            "Unique values": 4,
            "Mode (Most frequent)": "a",
            "Maximum frequency": 2,
        }

        assert self.majority_repeating._get_most_common().to_dict() == {
            "a": "3 (25.00%)",
            "b": "3 (25.00%)",
            "c": "3 (25.00%)",
            "d": "3 (25.00%)",
        }
        assert self.majority_repeating._get_summary_statistics().to_dict() == {
            "Number of observations": 12,
            "Unique values": 4,
            "Mode (Most frequent)": "a",
            "Maximum frequency": 3,
        }

    def test_repr(self):
        assert str(self.majority_unique) == (
            "\t\tOverview\n\t\t========\nName: None\nType: categorical\n"
            "Number of Observations: 6\n"
            "Unique Values: 4 -> ['a', 'b', 'c', 'd']\n"
            "Missing Values: 1 (16.67%)\n\n\t  Most Common Items\n\t  "
            "-----------------\n             \na  2 (33.33%)\nb  1 "
            "(16.67%)\nc  1 (16.67%)\nd  1 (16.67%)"
        )


class TestBooleanVariables:
    # Boolean variables are treated as categorical. Only the var_type differs.
    boolean_from_int = CategoricalVariable([1, 0, 1] * 5)
    boolean_variable = CategoricalVariable([True, False, True] * 5)

    def test_dtype(self):
        assert is_categorical_dtype(self.boolean_from_int.data)
        assert is_categorical_dtype(self.boolean_variable.data)
        assert self.boolean_from_int.var_type == "boolean"
        assert self.boolean_variable.var_type == "boolean"


class TestDateTimeVariables:

    variable = DatetimeVariable(
        date_range("01-01-2022", periods=10, freq="D"), name="dates"
    )

    def test_data_type(self):
        assert is_datetime64_any_dtype(self.variable.data)
        assert self.variable.var_type == "datetime"

    def test_summary_statistics(self):
        assert self.variable._get_summary_statistics().to_dict() == {
            "Number of observations": 10,
            "Average": Timestamp("2022-01-05 12:00:00"),
            "Minimum": Timestamp("2022-01-01 00:00:00"),
            "Lower Quartile": Timestamp("2022-01-03 06:00:00"),
            "Median": Timestamp("2022-01-05 12:00:00"),
            "Upper Quartile": Timestamp("2022-01-07 18:00:00"),
            "Maximum": Timestamp("2022-01-10 00:00:00"),
        }

    def test_repr(self):
        assert str(self.variable) == (
            "\t\tOverview\n\t\t========\nName: dates\nType: datetime\n"
            "Number of Observations: 10\nMissing Values: None\n\n\t  "
            "Summary Statistics\n\t  ------------------\n                   "
            "                        \nNumber of observations               "
            "    10\nAverage                 2022-01-05 12:00:00\nMinimum   "
            "              2022-01-01 00:00:00\nLower Quartile          "
            "2022-01-03 06:00:00\nMedian                  2022-01-05 12:00:00"
            "\nUpper Quartile          2022-01-07 18:00:00\nMaximum          "
            "       2022-01-10 00:00:00"
        )


class TestNumericVariables:

    variable = NumericVariable(data=range(50), name="1 to 50")

    def test_data_type(self):
        assert is_numeric_dtype(self.variable.data)
        assert self.variable.var_type == "numeric"

    def test_summary_statistics(self):
        assert (
            self.variable._get_summary_statistics().to_dict()
            == pytest.approx(
                {
                    "Number of observations": 50.0,
                    "Average": 24.5,
                    "Standard Deviation": 14.5773797,
                    "Minimum": 0.0,
                    "Lower Quartile": 12.25,
                    "Median": 24.5,
                    "Upper Quartile": 36.75,
                    "Maximum": 49.0,
                    "Skewness": 0.0,
                    "Kurtosis": -1.2,
                }
            )
        )

    def test_repr(self):
        pass
        # assert str(self.variable) == (
        #     "\t\tOverview\n\t\t========\nName: 1 to 50\nType: numeric\n"
        #     "Unique Values: 50 -> [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,"
        #     " 12, 13, [...]\nMissing Values: None\n\t\t  ***\n\t  Summary"
        #     " Statistics\n                         1 to 50\nNumber of "
        #     "observations  50.00000\nAverage                 24.50000\n"
        #     "Standard Deviation      14.57738\nMinimum                  "
        #     "0.00000\nLower Quartile          12.25000\nMedian           "
        #     "       24.50000\nUpper Quartile          36.75000\nMaximum"
        #     "                 49.00000\nSkewness                 "
        #     "0.00000\nKurtosis                -1.20000"
        # )
