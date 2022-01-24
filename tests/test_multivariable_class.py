from itertools import combinations

import pytest
from eda_report import summarize
from pandas import DataFrame


class TestMixedMultiVariables:

    multivariable = summarize(
        DataFrame(
            {
                "A": range(50),
                "B": list("abcdef") * 8 + ["a"] * 2,
                "C": [True, False] * 24 + [True] * 2,
                "D": [1, 3, 5, 7, 9, 11, 13] * 7 + [17],
            }
        )
    )

    def test_data_types(self):
        assert isinstance(self.multivariable.data, DataFrame)
        assert self.multivariable.categorical_cols.columns.to_list() == [
            "B",
            "C",
        ]
        assert self.multivariable.numeric_cols.columns.to_list() == ["A", "D"]

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

        expected = {
            "A": [1.0, 0.21019754169815527],
            "D": [0.21019754169815527, 1.0],
        }
        actual = self.multivariable.correlation_df.to_dict(orient="list")
        for key, values in actual.items():
            assert values == pytest.approx(expected[key])
        assert self.multivariable.correlation_descriptions == {
            ("A", "D"): "very weak positive correlation (0.21)"
        }

    def test_multivariable_description(self, capsys):
        self.multivariable.describe()
        captured = capsys.readouterr()
        assert captured.out == (
            "\n\tSummary Statistics (Numeric columns):\n\n    count  mean"
            "      std  min    25%   50%    75%   max  skewness  kurtosis\nA"
            "   50.0  24.5  14.5774  0.0  12.25  24.5  36.75  49.0    0.0000"
            "   -1.2000\nD   50.0   7.2   4.2426  1.0   3.00   7.0  11.00"
            "  17.0    0.1309   -0.9598\n\n\tSummary Statistics (Categorical"
            " columns):\n\n   count unique   top freq relative freq\nB    50"
            "      6     a   10        20.00%\nC    50      2  True   26"
            "        52.00%\n"
        )


class TestBivariateAnalysis:

    multivariable = summarize(
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

    def test_multivariable_attributes(self):
        assert self.multivariable.categorical_cols is None
        assert self.multivariable.categorical_stats is None
        assert self.multivariable.numeric_cols.columns.to_list() == list(
            "ABCDEFG"
        )
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

    def test_correlation(self):
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
            ("C", "E"): "weak positive correlation (0.49)",
            ("E", "F"): "weak negative correlation (-0.47)",
            ("B", "C"): "strong positive correlation (0.71)",
            ("A", "E"): "weak positive correlation (0.44)",
            ("D", "E"): "moderate positive correlation (0.59)",
            ("C", "G"): "very weak negative correlation (-0.21)",
            ("C", "F"): "weak negative correlation (-0.34)",
            ("C", "D"): "very strong positive correlation (0.92)",
            ("A", "G"): "virtually no correlation (-0.08)",
            ("B", "E"): "weak positive correlation (0.48)",
            ("D", "G"): "virtually no correlation (0.10)",
            ("A", "F"): "very weak negative correlation (-0.21)",
            ("D", "F"): "very weak negative correlation (-0.30)",
            ("A", "D"): "moderate positive correlation (0.63)",
            ("B", "G"): "virtually no correlation (-0.08)",
            ("A", "B"): "very strong positive correlation (0.98)",
            ("B", "F"): "weak negative correlation (-0.34)",
            ("B", "D"): "moderate positive correlation (0.64)",
            ("A", "C"): "strong positive correlation (0.71)",
            ("E", "G"): "very weak negative correlation (-0.10)",
        }

    def test_multivariable_description(self, capsys):
        self.multivariable.describe()
        captured = capsys.readouterr()
        assert captured.out == (
            "\n\tSummary Statistics (Numeric columns):\n\n    count  mean"
            "     std  min   25%  50%   75%  max  skewness  kurtosis\nA   "
            "10.0   4.5  3.0277  0.0  2.25  4.5  6.75  9.0    0.0000   "
            "-1.2000\nB   10.0   5.3  3.4010  0.0  2.50  6.0  8.00  9.0"
            "   -0.4271   -1.4977\nC   10.0   6.1  3.2128  0.0  4.25  7.5  "
            "8.75  9.0   -0.9167   -0.3921\nD   10.0   6.1  3.2128  2.0  2.50"
            "  7.5  9.00  9.0   -0.4644   -1.9554\nE   10.0   4.1  2.3781  "
            "2.0  2.00  4.0  4.75  9.0    1.0917    0.6123\nF   10.0   3.8  "
            "2.6583  0.0  2.00  3.5  4.75  9.0    0.7559    0.3744\nG   10.0"
            "   5.5  3.4075  0.0  3.25  6.0  8.75  9.0   -0.4528   -1.3223"
            "\n\nThere are no categorical columns.\n\n"
        )

    def test_bivariate_analysis_in_categorical_data(self, caplog, capsys):
        categorical_multivariable = summarize(["a", "b", "c"])

        assert str(categorical_multivariable) == (
            "\t\t\tOVERVIEW\n\t\t\t========\nNumeric features: \nCategorical"
            " features: var_1\n\t\t\t  ***\n\t  Summary Statistics (Numeric "
            "features)\n\t  -------------------------------------\nN/A"
            "\n\t\t\t  ***\n\t  Summary Statistics (Categorical features)\n\t"
            "  -----------------------------------------\n      count unique "
            "top freq relative freq\nvar_1     3      3   a    1        "
            "33.33%\n\t\t\t  ***\n\t  Bivariate Analysis (Correlation)\n\t  "
            "--------------------------------\nN/A"
        )
        assert (
            "Skipped Bivariate Analysis: "
            "Not enough numeric variables to compare."
        ) in caplog.text

        categorical_multivariable.describe()
        captured = capsys.readouterr()
        assert (
            "There are no numeric columns.\n\n\n\tSummary Statistics "
            "(Categorical columns):\n\n       count unique top freq relative"
            " freq\nvar_1     3      3   a    1        33.33%\n"
        ) in captured.out

    def test_bivariate_analysis_in_univariate_numeric_data(
        self, caplog, capsys
    ):
        numeric_1D = summarize(range(5))

        assert str(numeric_1D) == (
            "\t\t\tOVERVIEW\n\t\t\t========\nNumeric features: var_1\n"
            "Categorical features: \n\t\t\t  ***\n\t  Summary Statistics "
            "(Numeric features)\n\t  -------------------------------------\n"
            "       count  mean     std  min  25%  50%  75%  max  skewness  "
            "kurtosis\nvar_1    5.0   2.0  1.5811  0.0  1.0  2.0  3.0  4.0"
            "       0.0      -1.2\n\t\t\t  ***\n\t  Summary Statistics "
            "(Categorical features)\n\t  ----------------------------------"
            "-------\nN/A\n\t\t\t  ***\n\t  Bivariate Analysis (Correlation)"
            "\n\t  --------------------------------\nN/A"
        )
        assert (
            "Skipped Bivariate Analysis: "
            "Not enough numeric variables to compare."
        ) in caplog.text

        numeric_1D.describe()
        captured = capsys.readouterr()
        assert (
            "\n\tSummary Statistics (Numeric columns):\n\n        count  mean"
            "     std  min  25%  50%  75%  max  skewness  kurtosis\nvar_1    "
            "5.0   2.0  1.5811  0.0  1.0  2.0  3.0  4.0       0.0      -1.2"
            "\n\nThere are no categorical columns."
        ) in captured.out
