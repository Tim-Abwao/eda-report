from itertools import combinations

import pytest
from eda_report import summarize
from eda_report.multivariate import MultiVariable
from pandas import DataFrame


class TestMixedVariables:

    multivariable = MultiVariable(
        DataFrame(
            {
                "A": range(50),
                "B": list("abcdef") * 8 + ["a"] * 2,
                "C": [True, False] * 24 + [True] * 2,
                "D": [1, 3, 5, 7, 9, 11, 13] * 7 + [17],
            }
        )
    )

    def test_stored_data(self):
        assert isinstance(self.multivariable.data, DataFrame)
        assert list(self.multivariable.categorical_cols) == ["B", "C"]
        assert list(self.multivariable.numeric_cols) == ["A", "D"]

    def test_categorical_summary_statistics(self):
        assert self.multivariable.categorical_stats.to_dict() == {
            "count": {"B": 50, "C": 50},
            "unique": {"B": 6, "C": 2},
            "top": {"B": "a", "C": True},
            "freq": {"B": 10, "C": 26},
            "relative freq": {"B": "20.00%", "C": "52.00%"},
        }

    def test_numeric_summary_statistics(self):
        assert self.multivariable.numeric_stats.to_dict(
            orient="list"
        ) == pytest.approx(
            {
                "count": [50.0, 50.0],
                "mean": [24.5, 7.2],
                "std": [14.5774, 4.2426],
                "min": [0.0, 1.0],
                "25%": [12.25, 3.0],
                "50%": [24.5, 7.0],
                "75%": [36.75, 11.0],
                "max": [49.0, 17.0],
                "skewness": [0.0, 0.1309],
                "kurtosis": [-1.2, -0.9598],
            }
        )

    def test_correlation(self):
        assert self.multivariable.var_pairs == {("A", "D")}

        actual = self.multivariable.correlation_df.to_dict(orient="list")
        expected = {
            "A": [1.0, 0.21019754169815527],
            "D": [0.21019754169815527, 1.0],
        }
        for key, values in actual.items():
            assert values == pytest.approx(expected[key])
        assert self.multivariable.correlation_descriptions == {
            ("A", "D"): "weak positive correlation (0.21)"
        }

    def test_repr(self):
        assert str(self.multivariable) == (
            "\t\t\tOVERVIEW\n\t\t\t========\nNumeric features: A, D\n"
            "Categorical features: B, C\n\n\t  Summary Statistics (Numeric "
            "features)\n\t  -------------------------------------\n   count  "
            "mean      std  min    25%   50%    75%   max  skewness  kurtosis"
            "\nA   50.0  24.5  14.5774  0.0  12.25  24.5  36.75  49.0    "
            "0.0000   -1.2000\nD   50.0   7.2   4.2426  1.0   3.00   7.0  "
            "11.00  17.0    0.1309   -0.9598\n\n\t  Summary Statistics "
            "(Categorical features)\n\t  ------------------------------------"
            "-----\n  count unique   top freq relative freq\nB    50      6  "
            "   a   10        20.00%\nC    50      2  True   26        52.00%"
            "\n\n\t  Bivariate Analysis (Correlation)\n\t  ------------------"
            "--------------\nA & D --> weak positive correlation (0.21)"
        )


class TestNumericVariables:

    multivariable = MultiVariable(
        DataFrame(
            {
                "A": range(10),
                "B": [0, 1, 2, 4, 5, 7, 8, 8, 9, 9],
                "C": [0, 9, 2, 4, 5, 7, 8, 8, 9, 9],
                "D": [2, 9, 2, 2, 4, 9, 8, 7, 9, 9],
                "E": [2, 4, 2, 2, 4, 9, 2, 7, 4, 5],
                "F": [9, 4, 2, 5, 3, 0, 2, 2, 4, 7],
                "G": [9, 4, 9, 0, 3, 8, 7, 1, 9, 5],
            }
        )
    )

    def test_categorical_columns(self):
        assert self.multivariable.categorical_cols is None
        assert self.multivariable.categorical_stats is None

    def test_numeric_columns(self):
        assert list(self.multivariable.numeric_cols) == list("ABCDEFG")
        assert self.multivariable.numeric_stats.to_dict(
            orient="list"
        ) == pytest.approx(
            {
                "count": [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
                "mean": [4.5, 5.3, 6.1, 6.1, 4.1, 3.8, 5.5],
                "std": [3.0277, 3.401, 3.2128, 3.2128, 2.3781, 2.6583, 3.4075],
                "min": [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0],
                "25%": [2.25, 2.5, 4.25, 2.5, 2.0, 2.0, 3.25],
                "50%": [4.5, 6.0, 7.5, 7.5, 4.0, 3.5, 6.0],
                "75%": [6.75, 8.0, 8.75, 9.0, 4.75, 4.75, 8.75],
                "max": [9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
                "skewness": [
                    0.0,
                    -0.4271,
                    -0.9167,
                    -0.4644,
                    1.0917,
                    0.7559,
                    -0.4528,
                ],
                "kurtosis": [
                    -1.2,
                    -1.4977,
                    -0.3921,
                    -1.9554,
                    0.6123,
                    0.3744,
                    -1.3223,
                ],
            }
        )

    def test_bivariate_analysis(self):
        assert self.multivariable.var_pairs == set(
            combinations(["A", "B", "C", "D", "E", "F", "G"], 2)
        )
        actual = self.multivariable.correlation_df.to_dict(orient="list")
        expected = {
            "A": [
                1.0,
                0.9765539481257431,
                0.7139128286383059,
                0.6339545918308157,
                0.43980381734314006,
                -0.20707884164064558,
                -0.08077484696714896,
            ],
            "B": [
                0.9765539481257431,
                1.0000000000000002,
                0.7087605824155397,
                0.6375794622303348,
                0.4767000734763845,
                -0.33674149855122565,
                -0.08149583535198408,
            ],
            "C": [
                0.7139128286383059,
                0.7087605824155397,
                0.9999999999999997,
                0.9246501614639397,
                0.49298414273142294,
                -0.33564740289870953,
                -0.20805964772796604,
            ],
            "D": [
                0.6339545918308157,
                0.6375794622303348,
                0.9246501614639397,
                1.0,
                0.5947802783986784,
                -0.29661863511978975,
                0.0964178855324721,
            ],
            "E": [
                0.43980381734314006,
                0.4767000734763845,
                0.49298414273142294,
                0.5947802783986784,
                0.9999999999999999,
                -0.4710286732479611,
                -0.10283577538317387,
            ],
            "F": [
                -0.20707884164064558,
                -0.33674149855122565,
                -0.33564740289870953,
                -0.29661863511978975,
                -0.4710286732479611,
                1.0,
                0.024532583890697804,
            ],
            "G": [
                -0.08077484696714896,
                -0.08149583535198408,
                -0.20805964772796604,
                0.0964178855324721,
                -0.10283577538317387,
                0.024532583890697804,
                1.0,
            ],
        }
        for key, values in actual.items():
            assert values == pytest.approx(expected[key])

        assert self.multivariable.correlation_descriptions == {
            ("F", "G"): "virtually no correlation (0.02)",
            ("C", "E"): "moderate positive correlation (0.49)",
            ("E", "F"): "moderate negative correlation (-0.47)",
            ("B", "C"): "strong positive correlation (0.71)",
            ("A", "E"): "moderate positive correlation (0.44)",
            ("D", "E"): "moderate positive correlation (0.59)",
            ("C", "G"): "weak negative correlation (-0.21)",
            ("C", "F"): "weak negative correlation (-0.34)",
            ("C", "D"): "very strong positive correlation (0.92)",
            ("A", "G"): "very weak negative correlation (-0.08)",
            ("B", "E"): "moderate positive correlation (0.48)",
            ("D", "G"): "very weak positive correlation (0.10)",
            ("A", "F"): "weak negative correlation (-0.21)",
            ("D", "F"): "weak negative correlation (-0.30)",
            ("A", "D"): "strong positive correlation (0.63)",
            ("B", "G"): "very weak negative correlation (-0.08)",
            ("A", "B"): "very strong positive correlation (0.98)",
            ("B", "F"): "weak negative correlation (-0.34)",
            ("B", "D"): "strong positive correlation (0.64)",
            ("A", "C"): "strong positive correlation (0.71)",
            ("E", "G"): "very weak negative correlation (-0.10)",
        }


class TestCategoricalVariables:
    multivariable = MultiVariable(
        DataFrame([list("abcd")] * 4, columns=list("ABCD"))
    )

    def test_categorical_columns(self):
        assert list(self.multivariable.categorical_cols) == list("ABCD")
        assert self.multivariable.categorical_stats.to_dict(orient="list") == {
            "count": [4, 4, 4, 4],
            "unique": [1, 1, 1, 1],
            "top": ["a", "b", "c", "d"],
            "freq": [4, 4, 4, 4],
            "relative freq": ["100.00%", "100.00%", "100.00%", "100.00%"],
        }

    def test_numeric_columns(self):
        assert self.multivariable.numeric_cols is None
        assert self.multivariable.numeric_stats is None

    def test_bivariate_analysis(self, caplog):
        multivariable = MultiVariable([list("abcd")] * 4)
        assert (
            "Skipped Bivariate Analysis: There are less than 2 numeric "
            "variables having > 5% unique values."
        ) in caplog.text
        assert str(multivariable) == (
            "\t\t\tOVERVIEW\n\t\t\t========\n\nCategorical features: var_1, "
            "var_2, var_3, var_4\n\n\n\t  Summary Statistics (Categorical "
            "features)\n\t  -----------------------------------------\n      "
            "count unique top freq relative freq\nvar_1     4      1   a    4"
            "       100.00%\nvar_2     4      1   b    4       100.00%\nvar_3"
            "     4      1   c    4       100.00%\nvar_4     4      1   d    "
            "4       100.00%\n"
        )


class TestInsufficientNumericPairs:
    def test_1d_numeric(self, caplog):
        numeric_1D = MultiVariable(range(50))
        assert (
            "Skipped Bivariate Analysis: There are less than 2 numeric "
            "variables having > 5% unique values."
        ) in str(caplog.text)

        assert str(numeric_1D) == (
            "\t\tOverview\n\t\t========\nName: var_1\nType: numeric\nUnique "
            "Values: 50 -> [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, "
            "[...]\nMissing Values: None\n\n\t  Summary Statistics\n\t  "
            "------------------\n                                \nNumber of"
            " observations  50.00000\nAverage                 24.50000\n"
            "Standard Deviation      14.57738\nMinimum                  "
            "0.00000\nLower Quartile          12.25000\nMedian               "
            "   24.50000\nUpper Quartile          36.75000\nMaximum          "
            "       49.00000\nSkewness                 0.00000\nKurtosis     "
            "           -1.20000\n\n\t  Tests for Normality\n\t  ------------"
            "-------\n                               p-value Conclusion at α "
            "= 0.05\nD'Agostino's K-squared test  0.0015981  Unlikely to be "
            "normal\nKolmogorov-Smirnov test      0.0000000  Unlikely to be "
            "normal\nShapiro-Wilk test            0.0580895        Possibly "
            "normal"
        )

    def test_omitted_numeric(self):
        multivariable = MultiVariable(
            {"A": [1, 2] * 25, "B": range(50), "C": range(2, 101, 2)}
        )
        # Check that A (0.04% unique, < 0.05 threshold) is excluded
        assert multivariable.var_pairs == {("B", "C")}
        assert multivariable.correlation_descriptions == {
            ("B", "C"): "very strong positive correlation (1.00)"
        }

        assert str(multivariable) == (
            "\t\t\tOVERVIEW\n\t\t\t========\nNumeric features: A, B, C\n\n\n\t"
            "  Summary Statistics (Numeric features)\n\t  -------------------"
            "------------------\n   count  mean      std  min    25%   50%    "
            "75%    max  skewness  kurtosis\nA   50.0   1.5   0.5051  1.0   "
            "1.00   1.5   2.00    2.0       0.0   -2.0851\nB   50.0  24.5  "
            "14.5774  0.0  12.25  24.5  36.75   49.0       0.0   -1.2000\nC   "
            "50.0  51.0  29.1548  2.0  26.50  51.0  75.50  100.0       0.0   "
            "-1.2000\n\n\n\t  Bivariate Analysis (Correlation)\n\t  ---------"
            "-----------------------\nB & C --> very strong positive "
            "correlation (1.00)"
        )


def test_summarize_function():
    summary = summarize(range(15))
    assert isinstance(summary, MultiVariable)
