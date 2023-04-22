import pytest
from pandas import DataFrame, Timestamp, date_range

from eda_report.univariate import Variable, _analyze_univariate


class TestDtypeDetection:
    def test_bool_detection(self):
        boolean = Variable([True, False, True])
        assert boolean.var_type == "boolean"

    def test_categorical_detection(self):
        categorical = Variable(list("abcdefg"))
        assert categorical.var_type == "categorical"

    def test_datetime_detection(self):
        datetime = Variable(date_range("2022-01-01", periods=5, freq="D"))
        assert datetime.var_type == "datetime"

    def test_numeric_detection(self):
        numeric = Variable(range(20))
        assert numeric.var_type == "numeric"


class TestGeneralVariableProperties:
    variable = Variable(list(range(20)) + [None], name="some-variable")
    unnamed_variable = Variable(list("ababdea"))

    def test_missing_values(self):
        assert self.variable.missing == "1 (4.76%)"
        assert self.variable._num_non_null == 20
        assert self.unnamed_variable.missing is None
        assert self.unnamed_variable._num_non_null == 7

    def test_name(self):
        assert self.variable.name == "some-variable"
        assert self.unnamed_variable.name is None

    def test_renaming(self):
        self.unnamed_variable.rename(name="new name")
        assert self.unnamed_variable.name == "new name"

        self.variable.rename("another new name")
        assert self.variable.name == "another new name"

    def test_unique_values(self):
        assert self.variable.num_unique == 20
        assert self.variable.unique_values == pytest.approx(list(range(20)))

        assert self.unnamed_variable.num_unique == 4
        assert self.unnamed_variable.unique_values == list("abde")


class TestCategoricalVariables:
    categorical_variable = Variable(["a", "b", "c", "d", None, "a"])
    # Numeric variables with less than 10 unique values are treated as
    # categorical.
    numeric_categories = Variable([1, 2, 3] * 10)

    def test_variable_type(self):
        assert self.categorical_variable.var_type == "categorical"
        assert self.numeric_categories.var_type == "numeric (<10 levels)"

    def test_summary_statistics(self):
        assert self.categorical_variable.summary_stats == {
            "Mode (Most frequent)": "a",
            "Maximum frequency": 2,
        }

    def test_normality_results(self):
        assert self.categorical_variable._normality_test_results is None
        assert self.numeric_categories._normality_test_results is None

    def test_repr(self):
        assert str(self.categorical_variable) == (
            "\nName: None\nType: categorical\nNon-null Observations: 5\n"
            "Unique Values: 4 -> ['a', 'b', 'c', 'd']\nMissing Values: 1 "
            "(16.67%)\n\n\t\t  Summary Statistics\n\t\t  -----------------"
            "-\n\tMode (Most frequent):               a\n\tMaximum "
            "frequency:                  2"
        )


class TestBooleanVariables:
    # Boolean variables are treated as categorical. Only the var_type differs.
    boolean_variable = Variable([True, False, True, None] * 5)
    numeric_bool = Variable([1, 0, 1, None] * 5)
    str_bool_1 = Variable(["Yes", "No", "Yes"] * 5)
    str_bool_2 = Variable(["Y", "N", "Y"] * 5)

    def test_dtype(self):
        assert self.boolean_variable.var_type == "boolean"
        assert self.numeric_bool.var_type == "boolean"
        assert self.str_bool_1.var_type == "boolean"
        assert self.str_bool_2.var_type == "boolean"


class TestDateTimeVariables:
    datetime_variable = Variable(
        date_range("01-01-2022", periods=10, freq="D"), name="dates"
    )

    def test_variable_type(self):
        assert self.datetime_variable.var_type == "datetime"

    def test_summary_statistics(self):
        assert self.datetime_variable.summary_stats == {
            "Average": Timestamp("2022-01-05 12:00:00"),
            "Minimum": Timestamp("2022-01-01 00:00:00"),
            "Lower Quartile": Timestamp("2022-01-03 06:00:00"),
            "Median": Timestamp("2022-01-05 12:00:00"),
            "Upper Quartile": Timestamp("2022-01-07 18:00:00"),
            "Maximum": Timestamp("2022-01-10 00:00:00"),
        }

    def test_normality_results(self):
        assert self.datetime_variable._normality_test_results is None

    def test_repr(self):
        assert str(self.datetime_variable) == (
            "\nName: dates\nType: datetime\nNon-null Observations: 10\nUnique"
            " Values: 10 -> [Timestamp('2022-01-01 00:00:00'), [...]\nMissing"
            " Values: None\n\n\t\t  Summary Statistics\n\t\t  ---------------"
            "---\n\tAverage:              2022-01-05 12:00:00\n\tMinimum:    "
            "          2022-01-01 00:00:00\n\tLower Quartile:       "
            "2022-01-03 06:00:00\n\tMedian:               2022-01-05 12:00:00"
            "\n\tUpper Quartile:       2022-01-07 18:00:00\n\tMaximum:       "
            "       2022-01-10 00:00:00"
        )


class TestNumericVariable:
    numeric_variable = Variable(data=range(50), name="1 to 50")

    def test_variable_type(self):
        assert self.numeric_variable.var_type == "numeric"

    def test_summary_statistics(self):
        assert self.numeric_variable.summary_stats == pytest.approx(
            {
                "Average": 24.5,
                "Standard Deviation": 14.577379737113251,
                "Minimum": 0.0,
                "Lower Quartile": 12.25,
                "Median": 24.5,
                "Upper Quartile": 36.75,
                "Maximum": 49.0,
                "Skewness": 0.0,
                "Kurtosis": -1.2,
            }
        )

    def test_normality_results(self):
        assert isinstance(
            self.numeric_variable._normality_test_results, DataFrame
        )
        assert self.numeric_variable._normality_test_results.to_dict() == {
            "p-value": {
                "D'Agostino's K-squared test": "0.0015981",
                "Kolmogorov-Smirnov test": "0.0000000",
                "Shapiro-Wilk test": "0.0580895",
            },
            "Conclusion at α = 0.05": {
                "D'Agostino's K-squared test": "Unlikely to be normal",
                "Kolmogorov-Smirnov test": "Unlikely to be normal",
                "Shapiro-Wilk test": "Possibly normal",
            },
        }

    def test_repr(self):
        assert str(self.numeric_variable) == (
            "\nName: 1 to 50\nType: numeric\nNon-null Observations: 50\n"
            "Unique Values: 50 -> [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, "
            "13, [...]\nMissing Values: None\n\n\t\t  Summary Statistics\n\t"
            "\t  ------------------\n\tAverage:                      24.5000"
            "\n\tStandard Deviation:           14.5774\n\tMinimum:           "
            "            0.0000\n\tLower Quartile:               12.2500\n\t"
            "Median:                       24.5000\n\tUpper Quartile:        "
            "       36.7500\n\tMaximum:                      49.0000\n\t"
            "Skewness:                      0.0000\n\tKurtosis:              "
            "       -1.2000\n\n\t\t  Tests for Normality\n\t\t  -------------"
            "------\n                               p-value Conclusion at α ="
            " 0.05\nD'Agostino's K-squared test  0.0015981  Unlikely to be "
            "normal\nKolmogorov-Smirnov test      0.0000000  Unlikely to be "
            "normal\nShapiro-Wilk test            0.0580895        Possibly "
            "normal"
        )


def test_analyse_variable():
    name, variable = _analyze_univariate(("wantufifty", range(50)))

    assert name == "wantufifty"
    assert isinstance(variable, Variable)
