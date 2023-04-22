import pytest
from pandas import DataFrame

from eda_report.bivariate import (
    Dataset,
    _compute_correlation,
    _describe_correlation,
)

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


class TestDataset:
    dataset = Dataset(sample_data.copy())

    def test_stored_data(self):
        assert isinstance(self.dataset.data, DataFrame)

    def test_categorical_summary_statistics(self):
        assert self.dataset._categorical_stats.to_dict() == {
            "count": {"B": 50, "C": 50, "D": 50},
            "unique": {"B": 6, "C": 2, "D": 8},
            "top": {"B": "a", "C": True, "D": 1},
            "freq": {"B": 10, "C": 26, "D": 7},
            "relative freq": {"B": "20.00%", "C": "52.00%", "D": "14.00%"},
        }

    def test_numeric_summary_statistics(self):
        assert self.dataset._numeric_stats.to_dict(
            orient="list"
        ) == pytest.approx(
            {
                "count": [50.0],
                "mean": [24.5],
                "std": [14.5774],
                "min": [0.0],
                "25%": [12.25],
                "50%": [24.5],
                "75%": [36.75],
                "max": [49.0],
                "skewness": [0.0],
                "kurtosis": [-1.2],
            }
        )

    def test_correlation(self):
        assert self.dataset._correlation_values == pytest.approx(
            [(("A", "D"), 0.21019754169815516)]
        )
        assert self.dataset._correlation_descriptions == {
            ("A", "D"): "weak positive correlation (0.21)"
        }

    def test_repr(self):
        assert str(self.dataset) == (
            "\t\t\tOVERVIEW\n\t\t\t========\nNumeric features: A\nCategorical"
            " features: B, C, D\n\n\t  Summary Statistics (Numeric features)"
            "\n\t  -------------------------------------\n   count  mean     "
            " std  min    25%   50%    75%   max  skewness  kurtosis\nA   "
            "50.0  24.5  14.5774  0.0  12.25  24.5  36.75  49.0       0.0    "
            "  -1.2\n\n\t  Summary Statistics (Categorical features)\n\t  ---"
            "--------------------------------------\n  count unique   top "
            "freq relative freq\nB    50      6     a   10        20.00%\nC  "
            "  50      2  True   26        52.00%\nD    50      8     1    7 "
            "       14.00%\n\n\t  Pearson's Correlation (Top 20)\n\t  -------"
            "-----------------------\nA & D --> weak positive correlation "
            "(0.21)"
        )

    def test_numeric_only_repr(self):
        numeric_only = Dataset(sample_data[["A"]])
        assert str(numeric_only) == (
            "\t\t\tOVERVIEW\n\t\t\t========\nNumeric features: A\n\n\n\t  "
            "Summary Statistics (Numeric features)\n\t  ---------------------"
            "----------------\n   count  mean      std  min    25%   50%    "
            "75%   max  skewness  kurtosis\nA   50.0  24.5  14.5774  0.0  "
            "12.25  24.5  36.75  49.0       0.0      -1.2\n\n"
        )

    def test_categorical_only_repr(self, caplog: pytest.LogCaptureFixture):
        categorical_only = Dataset(sample_data[["B", "C"]])
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

    def test_correlation_info_truncation_(self):
        plenty_numeric = Dataset(
            DataFrame(
                {
                    "A": range(11),
                    "B": [0, 1, 2, 4, 5, 7, 8, 8, 9, 9, 4],
                    "C": [0, 9, 2, 4, 5, 7, 8, 8, 9, 9, 1],
                    "D": [2, 9, 2, 2, 4, 9, 8, 7, 9, 9, 3],
                    "E": [2, 4, 2, 2, 4, 9, 2, 7, 4, 5, 8],
                    "F": [9, 4, 2, 5, 3, 0, 2, 2, 4, 7, 6],
                    "G": [9, 4, 9, 0, 3, 8, 7, 1, 9, 5, 2],
                }
            )
        )
        # In particular, only the top 20 correlation descriptions are should
        # be displayed.
        assert len(plenty_numeric._correlation_descriptions) == 21
        assert str(plenty_numeric) == (
            "\t\t\tOVERVIEW\n\t\t\t========\nNumeric features: A\nCategorical"
            " features: B, C, D, E, F, G\n\n\t  Summary Statistics (Numeric "
            "features)\n\t  -------------------------------------\n   count  "
            "mean     std  min  25%  50%  75%   max  skewness  kurtosis\nA   "
            "11.0   5.0  3.3166  0.0  2.5  5.0  7.5  10.0       0.0      -1.2"
            "\n\n\t  Summary Statistics (Categorical features)\n\t  ---------"
            "--------------------------------\n  count unique top freq "
            "relative freq\nB    11      8   4    2        18.18%\nC    11   "
            "   8   9    3        27.27%\nD    11      6   9    4        "
            "36.36%\nE    11      6   2    4        36.36%\nF    11      8   "
            "2    3        27.27%\nG    11      9   9    3        27.27%\n\n"
            "\t  Pearson's Correlation (Top 20)\n\t  ------------------------"
            "------\nC & D --> very strong positive correlation (0.92)\nA & B"
            " --> strong positive correlation (0.78)\nB & C --> strong "
            "positive correlation (0.68)\nB & D --> strong positive "
            "correlation (0.64)\nA & E --> moderate positive correlation ("
            "0.57)\nC & F --> moderate negative correlation (-0.40)\nA & D --"
            "> weak positive correlation (0.38)\nD & E --> weak positive "
            "correlation (0.37)\nB & E --> weak positive correlation (0.36)\n"
            "B & F --> weak negative correlation (-0.35)\nD & F --> weak "
            "negative correlation (-0.35)\nA & C --> weak positive "
            "correlation (0.33)\nE & F --> weak negative correlation (-0.29)"
            "\nE & G --> weak negative correlation (-0.23)\nA & G --> weak "
            "negative correlation (-0.22)\nC & E --> very weak positive "
            "correlation (0.18)\nD & G --> very weak positive correlation "
            "(0.18)\nF & G --> very weak negative correlation (-0.06)\nA & F "
            "--> virtually no correlation (-0.05)\nB & G --> virtually no "
            "correlation (-0.04)"
        )
