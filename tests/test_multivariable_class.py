import unittest

import pandas as pd
from eda_report.multivariate import MultiVariable


class TestGeneralMultiVariableProperties(unittest.TestCase):

    def setUp(self):
        self.variables = MultiVariable(
            pd.DataFrame({'A': range(50),
                          'B': list('abcde') * 10,
                          'C': [True, False] * 25,
                          'D': [1, 3, 5, 7, 9] * 10})
        )

    def test_type_classification(self):
        # Check if features are correctly categorised
        self.assertEqual(
            self.variables.numeric_cols.columns.to_list(), ['A', 'D']
        )
        self.assertEqual(
            self.variables.categotical_cols.columns.to_list(), ['B', 'C']
        )

    def test_correlation_df(self):
        # Check if correlation is computed for numeric columns
        self.assertAlmostEqual(
            self.variables.correlation_df.loc['A', 'A'], 1
        )
        self.assertAlmostEqual(
            self.variables.correlation_df.loc['A', 'D'], 0.0979992
        )

    def test_graphs_plotted(self):
        # Check if the joint correlation plot is present
        self.assertIn(b'\x89PNG',
                      self.variables.joint_correlation_plot.getvalue())
        # Check if the joint scatterplot is present
        self.assertIn(b'\x89PNG', self.variables.joint_scatterplot.getvalue())
        # Check if numerical variable pairwise scatterplots are present
        self.assertIn(
            b'\x89PNG',
            self.variables.bivariate_scatterplots[('A', 'D')].getvalue())


class TestBivariateAnalysis(unittest.TestCase):

    def setUp(self):
        self.variables = MultiVariable(
            pd.DataFrame({
                'A': range(10),
                'B': [0, 1, 2, 4, 5, 7, 8, 8, 9, 9],
                'C': [0, 9, 2, 4, 5, 7, 8, 8, 9, 9],
                'D': [2, 9, 2, 2, 4, 9, 8, 7, 9, 9],
                'E': [2, 4, 2, 2, 4, 9, 2, 7, 4, 5],
                'F': [9, 4, 2, 5, 3, 0, 2, 2, 4, 7],
                'G': [9, 4, 9, 0, 3, 8, 7, 1, 9, 5]})
        )

    def test_variable_pairs(self):
        # Check if numerical variable pairs are correctly collected
        self.assertEqual(
            self.variables.var_pairs,
            {('A', 'B'), ('A', 'C'), ('A', 'D'), ('A', 'E'), ('A', 'F'),
             ('A', 'G'), ('B', 'C'), ('B', 'D'), ('B', 'E'), ('B', 'F'),
             ('B', 'G'), ('C', 'D'), ('C', 'E'), ('C', 'F'), ('C', 'G'),
             ('D', 'E'), ('D', 'F'), ('D', 'G'), ('E', 'F'), ('E', 'G'),
             ('F', 'G')}
        )

    def test_correlation_description(self):
        self.assertEqual(
            'very strong positive correlation (0.98)',
            self.variables.corr_type[('A', 'B')]
        )
        self.assertEqual(
            'strong positive correlation (0.71)',
            self.variables.corr_type[('A', 'C')]
        )
        self.assertEqual(
            'moderate positive correlation (0.63)',
            self.variables.corr_type[('A', 'D')]
        )
        self.assertEqual(
            'weak positive correlation (0.44)',
            self.variables.corr_type[('A', 'E')]
        )
        self.assertEqual(
            'very weak negative correlation (-0.21)',
            self.variables.corr_type[('A', 'F')]
        )
        self.assertEqual(
            'virtually no correlation (-0.08)',
            self.variables.corr_type[('A', 'G')]
        )
