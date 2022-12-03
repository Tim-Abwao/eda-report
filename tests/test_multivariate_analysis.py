import pytest
from eda_report import summarize
from eda_report.multivariate import (
    MultiVariable,
    _describe_correlation,
    _compute_correlation,
    _select_dtypes,
)
from pandas import DataFrame

sample_data = DataFrame(
    {
        "A": range(50),
        "B": list("abcdef") * 8 + ["a"] * 2,
        "C": [True, False] * 24 + [True] * 2,
        "D": [1, 3, 5, 7, 9, 11, 13] * 7 + [17],
    }
)


def test_correlation_computation():
    data = sample_data.copy()
    assert _compute_correlation(None) is None

    # Check that < 2 numeric cols returns None
    assert _compute_correlation(data[["A", "B"]]) is None

    # Check that only numeric columns are processed
    assert _compute_correlation(data) == pytest.approx(
        [(("A", "D"), 0.21019754169815516)]
    )


def test_correlation_description():
    assert (
        _describe_correlation(0.9) == "very strong positive correlation (0.90)"
    )
    assert _describe_correlation(-0.7) == "strong negative correlation (-0.70)"
    assert _describe_correlation(0.5) == "moderate positive correlation (0.50)"
    assert _describe_correlation(-0.3) == "weak negative correlation (-0.30)"
    assert (
        _describe_correlation(0.1) == "very weak positive correlation (0.10)"
    )
    assert _describe_correlation(0.025) == "virtually no correlation (0.03)"


def test_dtype_selection():
    data = sample_data.copy()

    assert _select_dtypes(data, "number").columns.to_list() == ["A", "D"]
    assert _select_dtypes(
        data, "bool", "category", "object"
    ).columns.to_list() == ["B", "C"]

    # Check that None is returned if dtype is not present
    assert _select_dtypes(data[["B", "C"]], "number") is None
    assert (
        _select_dtypes(data[["A", "D"]], "bool", "category", "object") is None
    )


class TestMultiVariable:

    multivariable = MultiVariable(sample_data.copy())

    def test_stored_data(self):
        assert isinstance(self.multivariable.data, DataFrame)

    def test_categorical_summary_statistics(self):
        assert self.multivariable._categorical_stats.to_dict() == {
            "count": {"B": 50, "C": 50},
            "unique": {"B": 6, "C": 2},
            "top": {"B": "a", "C": True},
            "freq": {"B": 10, "C": 26},
            "relative freq": {"B": "20.00%", "C": "52.00%"},
        }

    def test_numeric_summary_statistics(self):
        assert self.multivariable._numeric_stats.to_dict(
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
        assert self.multivariable._correlation_values == pytest.approx(
            [(("A", "D"), 0.21019754169815516)]
        )
        assert self.multivariable._correlation_descriptions == {
            ("A", "D"): "weak positive correlation (0.21)"
        }

    def test_repr(self):
        assert str(self.multivariable) == (
            "\t\t\tOVERVIEW\n\t\t\t========\nNumeric features: A, D\n"
            "Categorical features: B, C\n\n\t  Summary Statistics "
            "(Numeric features)\n\t  -------------------------------------\n"
            "   count  mean      std  min    25%   50%    75%   max  skewness"
            "  kurtosis\nA   50.0  24.5  14.5774  0.0  12.25  24.5  36.75  "
            "49.0    0.0000   -1.2000\nD   50.0   7.2   4.2426  1.0   3.00   "
            "7.0  11.00  17.0    0.1309   -0.9598\n\n\t  Summary Statistics "
            "(Categorical features)\n\t  ------------------------------------"
            "-----\n  count unique   top freq relative freq\nB    50      6  "
            "   a   10        20.00%\nC    50      2  True   26        52.00%"
            "\n\n\t  Pearson's Correlation (Top 20)\n\t  --------------------"
            "----------\nA & D --> weak positive correlation (0.21)"
        )

    def test_numeric_only_repr(self):
        numeric_only = MultiVariable(sample_data[["A", "D"]])
        assert str(numeric_only) == (
            "\t\t\tOVERVIEW\n\t\t\t========\nNumeric features: A, D\n\n\n\t  "
            "Summary Statistics (Numeric features)\n\t  "
            "-------------------------------------\n   "
            "count  mean      std  min    25%   50%    75%   max  skewness  "
            "kurtosis\nA   50.0  24.5  14.5774  0.0  12.25  24.5  36.75  49.0"
            "    0.0000   -1.2000\nD   50.0   7.2   4.2426  1.0   3.00   7.0"
            "  11.00  17.0    0.1309   -0.9598\n\n\n\t  "
            "Pearson's Correlation (Top 20)\n\t  "
            "------------------------------\n"
            "A & D --> weak positive correlation (0.21)"
        )

    def test_categorical_only_repr(self, caplog):
        categorical_only = MultiVariable(sample_data[["B", "C"]])
        assert (
            "Skipped Bivariate Analysis: There are less than 2 numeric "
            "variables."
        ) in str(caplog.text)
        assert str(categorical_only) == (
            "\t\t\tOVERVIEW\n\t\t\t========\n\n"
            "Categorical features: B, C\n\n\n\t  "
            "Summary Statistics (Categorical features)\n\t  "
            "-----------------------------------------\n  "
            "count unique   top freq relative freq\nB    "
            "50      6     a   10        20.00%\n"
            "C    50      2  True   26        52.00%\n"
        )

    def test_1d_numeric(self, caplog):
        numeric_1D = MultiVariable(range(50))
        assert (
            "Skipped Bivariate Analysis: There are less than 2 numeric "
            "variables."
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

    def test_correlation_info_truncation_(self):
        plenty_numeric = MultiVariable(
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
        # In particular, only the top 20 correlation descriptions are should
        # be displayed.
        assert len(plenty_numeric._correlation_descriptions) == 21
        assert str(plenty_numeric) == (
            "\t\t\tOVERVIEW\n\t\t\t========\n"
            "Numeric features: A, B, C, D, E, F, G\n\n\n\t  "
            "Summary Statistics (Numeric features)\n\t  "
            "-------------------------------------\n   "
            "count  mean     std  min   25%  50%   75%  max  skewness  "
            "kurtosis\nA   10.0   4.5  3.0277  0.0  2.25  4.5  6.75  9.0    "
            "0.0000   -1.2000\nB   10.0   5.3  3.4010  0.0  2.50  6.0  8.00  "
            "9.0   -0.4271   -1.4977\nC   10.0   6.1  3.2128  0.0  4.25  7.5 "
            " 8.75  9.0   -0.9167   -0.3921\nD   10.0   6.1  3.2128  2.0  "
            "2.50  7.5  9.00  9.0   -0.4644   -1.9554\nE   10.0   4.1  2.3781"
            "  2.0  2.00  4.0  4.75  9.0    1.0917    0.6123\nF   10.0   3.8"
            "  2.6583  0.0  2.00  3.5  4.75  9.0    0.7559    0.3744\nG   "
            "10.0   5.5  3.4075  0.0  3.25  6.0  8.75  9.0   -0.4528   "
            "-1.3223\n\n\n\t  Pearson's Correlation (Top 20)\n\t  "
            "------------------------------\n"
            "A & B --> very strong positive correlation (0.98)\n"
            "C & D --> very strong positive correlation (0.92)\n"
            "A & C --> strong positive correlation (0.71)\n"
            "B & C --> strong positive correlation (0.71)\n"
            "B & D --> strong positive correlation (0.64)\n"
            "A & D --> strong positive correlation (0.63)\n"
            "D & E --> moderate positive correlation (0.59)\n"
            "C & E --> moderate positive correlation (0.49)\n"
            "B & E --> moderate positive correlation (0.48)\n"
            "E & F --> moderate negative correlation (-0.47)\n"
            "A & E --> moderate positive correlation (0.44)\n"
            "B & F --> weak negative correlation (-0.34)\n"
            "C & F --> weak negative correlation (-0.34)\n"
            "D & F --> weak negative correlation (-0.30)\n"
            "C & G --> weak negative correlation (-0.21)\n"
            "A & F --> weak negative correlation (-0.21)\n"
            "E & G --> very weak negative correlation (-0.10)\n"
            "D & G --> very weak positive correlation (0.10)\n"
            "B & G --> very weak negative correlation (-0.08)\n"
            "A & G --> very weak negative correlation (-0.08)"
        )


def test_summarize_function():
    summary = summarize(range(15))
    assert isinstance(summary, MultiVariable)
