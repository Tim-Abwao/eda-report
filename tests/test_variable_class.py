import pytest
from eda_report.univariate import Variable
from pandas import Series, date_range


class TestNumericVariables:

    variable = Variable(data=range(50), name="1 to 50")

    def test_data_type(self):
        assert isinstance(self.variable.data, Series)
        assert self.variable.data.dtype == int
        assert self.variable.var_type == "numeric"

    def test_missing_values(self):
        assert self.variable.missing is None

    def test_name(self):
        assert self.variable.name == "1 to 50"

    def test_unique_values(self):
        assert self.variable.num_unique == 50
        assert self.variable.unique == list(range(50))

    def test_summary_statistics(self):
        assert self.variable.statistics.to_dict()["1 to 50"] == pytest.approx(
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

    def test_repr(self):
        assert str(self.variable) == (
                "\t\tOverview\n\t\t========\nName: 1 to 50\nType: numeric\n"
                "Unique Values: 50 -> [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,"
                " 12, 13, [...]\nMissing Values: None\n\t\t  ***\n\t  Summary"
                " Statistics\n                         1 to 50\nNumber of "
                "observations  50.00000\nAverage                 24.50000\n"
                "Standard Deviation      14.57738\nMinimum                  "
                "0.00000\nLower Quartile          12.25000\nMedian           "
                "       24.50000\nUpper Quartile          36.75000\nMaximum"
                "                 49.00000\nSkewness                 "
                "0.00000\nKurtosis                -1.20000"
        )

    def test_numeric_variable_methods(self):
        self.variable.rename("new name")
        assert self.variable.name == "new name"


class TestCategoricalVariables:

    variable_with_majority_unique = Variable(["a", "b", "c", "d", None, "a"])
    variable_with_majority_repeating = Variable(["a", "b", "c", "d"] * 3)

    def test_data_type(self):

        assert isinstance(self.variable_with_majority_unique.data, Series)
        assert self.variable_with_majority_unique.data.dtype == "object"
        assert self.variable_with_majority_unique.var_type == "categorical"

        assert isinstance(self.variable_with_majority_repeating.data, Series)
        assert self.variable_with_majority_repeating.data.dtype == "category"
        assert self.variable_with_majority_repeating.var_type == "categorical"

    def test_missing_values(self):
        assert self.variable_with_majority_unique.missing == "1 (16.67%)"
        assert self.variable_with_majority_repeating.missing is None

    def test_name(self):
        assert self.variable_with_majority_unique.name is None
        assert self.variable_with_majority_repeating.name is None

    def test_unique_values(self):
        assert self.variable_with_majority_unique.num_unique == 4
        assert self.variable_with_majority_unique.unique == list("abcd")

        assert self.variable_with_majority_repeating.num_unique == 4
        assert self.variable_with_majority_repeating.unique == list("abcd")

    def test_summary_statistics(self):
        assert self.variable_with_majority_unique.most_common_items.to_dict()[
            0
        ] == {
            "a": "2 (33.33%)",
            "b": "1 (16.67%)",
            "c": "1 (16.67%)",
            "d": "1 (16.67%)",
        }
        assert self.variable_with_majority_unique.statistics.to_dict()[0] == {
            "Number of observations": 5,
            "Unique values": 4,
            "Mode (Highest occurring value)": "a",
        }

        assert (
            self.variable_with_majority_repeating.most_common_items.to_dict()[
                0
            ]
            == {
                "a": "3 (25.00%)",
                "b": "3 (25.00%)",
                "c": "3 (25.00%)",
                "d": "3 (25.00%)",
            }
        )
        assert self.variable_with_majority_repeating.statistics.to_dict()[
            0
        ] == {
            "Number of observations": 12,
            "Unique values": 4,
            "Mode (Highest occurring value)": "a",
        }

    def test_repr(self):
        assert str(self.variable_with_majority_unique) == (
            "\t\tOverview\n\t\t========\nName: None\nType: categorical\n"
            "Unique Values: 4 -> ['a', 'b', 'c', 'd']\nMissing Values: 1 "
            "(16.67%)\n\t\t  ***\n\t  Summary Statistics\n                "
            "                0\nNumber of observations          5\nUnique"
            " values                   4\nMode (Highest occurring value)  a"
            )

    def test_categorical_variable_methods(self):
        self.variable_with_majority_unique.rename("new name")
        assert self.variable_with_majority_unique.name == "new name"
        self.variable_with_majority_unique.rename()
        assert self.variable_with_majority_unique.name is None


class TestBooleanVariables:

    boolean_variable = Variable([True, True, False], name="bool vals")
    boolean_variable_from_int = Variable([0, 1, 1, None])

    def test_data_type(self):
        assert isinstance(self.boolean_variable.data, Series)
        assert self.boolean_variable.data.dtype == "object"
        assert self.boolean_variable.var_type == "boolean"

        assert isinstance(self.boolean_variable_from_int.data, Series)
        assert self.boolean_variable_from_int.data.dtype == "category"
        assert self.boolean_variable_from_int.var_type == "boolean"

    def test_missing_values(self):
        assert self.boolean_variable.missing is None
        assert self.boolean_variable_from_int.missing == "1 (25.00%)"

    def test_name(self):
        assert self.boolean_variable.name == "bool vals"
        assert self.boolean_variable_from_int.name is None

    def test_unique_values(self):
        assert self.boolean_variable.num_unique == 2
        assert self.boolean_variable.unique == [False, True]

        assert self.boolean_variable_from_int.num_unique == 2
        assert self.boolean_variable_from_int.unique == [0.0, 1.0]

    def test_summary_statistics(self):
        assert self.boolean_variable.most_common_items.to_dict()[
            "bool vals"
        ] == {
            True: "2 (66.67%)",
            False: "1 (33.33%)",
        }
        assert self.boolean_variable.statistics.to_dict()["bool vals"] == {
            "Number of observations": 3,
            "Unique values": 2,
            "Mode (Highest occurring value)": True,
        }

        assert self.boolean_variable_from_int.most_common_items.to_dict()[
            0
        ] == {1.0: "2 (50.00%)", 0.0: "1 (25.00%)"}
        assert self.boolean_variable_from_int.statistics.to_dict()[0] == {
            "Number of observations": 3.0,
            "Unique values": 2.0,
            "Mode (Highest occurring value)": 1.0,
        }


class TestDateTimeVariables:

    variable = Variable(
        date_range("01-01-2021", periods=10, freq="D"), name="dates"
    )

    def test_data_type(self):
        assert isinstance(self.variable.data, Series)
        assert self.variable.data.dtype == "object"
        assert self.variable.var_type == "datetime"

    def test_missing_values(self):
        assert self.variable.missing is None

    def test_name(self):
        assert self.variable.name == "dates"

    def test_unique_values(self):
        assert self.variable.num_unique == 10
        assert self.variable.unique == sorted(
            t.strftime("%c")
            for t in date_range("01-01-2021", periods=10, freq="D")
        )

    def test_summary_statistics(self):
        assert self.variable.most_common_items["dates"].to_list() == [
            "1 (10.00%)",
            "1 (10.00%)",
            "1 (10.00%)",
            "1 (10.00%)",
            "1 (10.00%)",
        ]

        assert self.variable.statistics[:-1].to_dict()["dates"] == {
            "Number of observations": 10,
            "Unique values": 10,
        }
