import pandas as pd
import unittest
from eda_report.multivariate import MultiVariable


class TestBivariateAnalysis(unittest.TestCase):

    def setUp(self):
        self.variables = MultiVariable(
            pd.DataFrame({'A': range(50),
                          'B': list('abcde') * 10,
                          'C': [0, 1] * 25,
                          'D': [1, 3, 5, 7, 9] * 10})
        )

    def test_variable_pairs(self):
        self.assertEqual(
            self.variables.var_pairs, {('A', 'C'), ('A', 'D'), ('C', 'D')}
        )

    def test_graphs_plotted(self):
        self.assertIn(b'\x89PNG',
                      self.variables.joint_correlation_plot.getvalue())
        self.assertIn(b'\x89PNG', self.variables.joint_scatterplot.getvalue())
        self.assertIn(
            b'\x89PNG',
            self.variables.bivariate_scatterplots[('A', 'C')].getvalue())

    def test_correlation_description(self):
        self.assertEqual(
            'virtually no correlation (0.03)',
            self.variables.corr_type[('A', 'C')]
        )
