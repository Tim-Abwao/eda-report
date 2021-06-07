import unittest

import pandas as pd
from eda_report.multivariate import MultiVariable


class TestGeneralMultiVariableProperties(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame(
            {
                "A": range(50),
                "B": list("abcdef") * 8 + ["a"] * 2,
                "C": [True, False] * 25,
                "D": [1, 3, 5, 7, 9] * 10,
            }
        )
        self.variables = MultiVariable(self.data)

    def test_type_classification(self):
        # Check if features are correctly categorised
        self.assertEqual(
            self.variables.numeric_cols.columns.to_list(), ["A", "D"]
        )
        self.assertEqual(
            self.variables.categorical_cols.columns.to_list(), ["B", "C"]
        )
        # Check if data with purely numeric features is handled
        numeric_variable = MultiVariable(self.variables.numeric_cols)
        self.assertIsNone(numeric_variable.categorical_cols)
        self.assertIn(
            "Categorical features: \n\n        Summary Statistics",
            repr(numeric_variable),
        )
        self.assertEqual(
            numeric_variable.numeric_cols.columns.to_list(),
            self.variables.numeric_cols.columns.to_list(),
        )
        # Check if data with purely categorical features is handled
        categorical_variable = MultiVariable(self.variables.categorical_cols)
        self.assertIsNone(categorical_variable.numeric_cols)
        self.assertIn(
            "Numeric features: \nCategorical features:",
            repr(categorical_variable),
        )
        self.assertEqual(
            categorical_variable.categorical_cols.columns.to_list(),
            self.variables.categorical_cols.columns.to_list(),
        )

    def test_correlation_df(self):
        # Check if correlation is computed for numeric columns
        self.assertAlmostEqual(self.variables.correlation_df.loc["A", "A"], 1)
        self.assertAlmostEqual(
            self.variables.correlation_df.loc["A", "D"], 0.0979992
        )

    def test_graphs_plotted(self):
        # Check if the joint correlation plot is present
        self.assertIn(
            b"\x89PNG", self.variables.joint_correlation_heatmap.getvalue()
        )
        # Check if the joint scatterplot is present
        self.assertIn(b"\x89PNG", self.variables.joint_scatterplot.getvalue())
        # Check if numerical variable pairwise scatterplots are present
        self.assertIn(
            b"\x89PNG",
            self.variables.bivariate_scatterplots[("A", "D")].getvalue(),
        )

    def test_repr(self):
        self.assertEqual(
            repr(self.variables),
            """\
        Overview
        ========
Numeric features: A, D
Categorical features: B, C

        Summary Statistics (Numeric features)
        =====================================
              A          D
count  50.00000  50.000000
mean   24.50000   5.000000
std    14.57738   2.857143
min     0.00000   1.000000
25%    12.25000   3.000000
50%    24.50000   5.000000
75%    36.75000   7.000000
max    49.00000   9.000000

        Summary Statistics (Categorical features)
        =========================================
         B      C
count   50     50
unique   6      2
top      a  False
freq    10     25

        Bivariate Analysis (Correlation)
        ================================
A & C --> virtually no correlation (-0.03)
A & D --> virtually no correlation (0.10)
C & D --> virtually no correlation (0.00)
""",
        )

    def test_valid_target_data(self):
        # A target variable valid for color-coding has 1 to 10 unique values
        with_numeric_target = MultiVariable(self.data, target_variable="D")
        with_categorical_target = MultiVariable(self.data, target_variable="B")
        self.assertEqual(
            with_numeric_target._COLOR_CODED_GRAPHS, {"joint-scatterplot"}
        )
        self.assertEqual(
            with_categorical_target._COLOR_CODED_GRAPHS, {"joint-scatterplot"}
        )

    def test_invalid_target_data(self):
        with self.assertLogs(level="WARNING") as logged_warning:
            X = MultiVariable(self.data, target_variable="A")
            # Check that invalid target is ignored
            self.assertEqual(X._COLOR_CODED_GRAPHS, set())
            # Check that the warning message is correct
            self.assertEqual(
                logged_warning.records[-1].message,
                "Target variable 'A' not used to group values in joint "
                "scatterplot. It has too many levels (50), and would clutter"
                " the graph.",
            )


class TestBivariateAnalysis(unittest.TestCase):
    def setUp(self):
        self.variables = MultiVariable(
            pd.DataFrame(
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

    def test_variable_pairs(self):
        # Check if numerical variable pairs are correctly collected
        self.assertEqual(
            self.variables.var_pairs,
            {
                ("A", "B"),
                ("A", "C"),
                ("A", "D"),
                ("A", "E"),
                ("A", "F"),
                ("A", "G"),
                ("B", "C"),
                ("B", "D"),
                ("B", "E"),
                ("B", "F"),
                ("B", "G"),
                ("C", "D"),
                ("C", "E"),
                ("C", "F"),
                ("C", "G"),
                ("D", "E"),
                ("D", "F"),
                ("D", "G"),
                ("E", "F"),
                ("E", "G"),
                ("F", "G"),
            },
        )

    def test_correlation_description(self):
        self.assertEqual(
            "very strong positive correlation (0.98)",
            self.variables.corr_type[("A", "B")],
        )
        self.assertEqual(
            "strong positive correlation (0.71)",
            self.variables.corr_type[("A", "C")],
        )
        self.assertEqual(
            "moderate positive correlation (0.63)",
            self.variables.corr_type[("A", "D")],
        )
        self.assertEqual(
            "weak positive correlation (0.44)",
            self.variables.corr_type[("A", "E")],
        )
        self.assertEqual(
            "very weak negative correlation (-0.21)",
            self.variables.corr_type[("A", "F")],
        )
        self.assertEqual(
            "virtually no correlation (-0.08)",
            self.variables.corr_type[("A", "G")],
        )
