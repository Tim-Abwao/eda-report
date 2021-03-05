import pandas as pd
import unittest
from eda_report.univariate import Variable


class TestVariableTypes(unittest.TestCase):

    def setUp(self):
        self.numeric_variable = Variable(
            pd.Series(range(50), name='numbers')
        )
        self.categorical_variable = Variable(
            pd.Series(list('abcd') * 12, name='letters')
        )
        self.boolean_variable = Variable(
            pd.Series([True, False, True] * 15, name='bool')
        )

    def test_numeric_variable(self):
        # Check if data type is numeric
        self.assertEqual(self.numeric_variable.var_type, 'numeric')
        # Check summary statistics
        self.assertEqual(
            self.numeric_variable.statistics.index.to_list(),
            ['Number of observations', 'Average', 'Standard Deviation',
             'Minimum', 'Lower Quartile', 'Median', 'Upper Quartile',
             'Maximum', 'Skewness', 'Kurtosis']
        )
        self.assertAlmostEqual(
            self.numeric_variable.statistics['Average'], 24.5
        )

    def test_categorical_variable(self):
        # Check if data type is categorical
        self.assertEqual(self.categorical_variable.var_type, 'categorical')
        # Check summary statistics
        self.assertEqual(
            self.categorical_variable.statistics.index.to_list(),
            ['Number of observations', 'Unique values',
             'Mode (Highest occurring value)']
        )
        self.assertEqual(
            self.categorical_variable.statistics['Unique values'], 4
        )

    def test_boolean_variable(self):
        # Check if data type is categorical
        self.assertEqual(self.boolean_variable.var_type, 'categorical')
        # Check summary statistics
        self.assertEqual(
            self.boolean_variable.statistics.index.to_list(),
            ['Number of observations', 'Unique values',
             'Mode (Highest occurring value)']
        )
        self.assertEqual(
            self.boolean_variable.statistics['Mode (Highest occurring value)'],
            True
        )


class TestVariableProperties(unittest.TestCase):

    def setUp(self):
        some_sample = pd.Series(range(50), name='some variable')
        some_sample.iloc[[0, 10, 20]] = None
        self.variable = Variable(some_sample)

    def test_variable_name(self):
        self.assertEqual(self.variable.name, 'some variable')

    def test_unique_values(self):
        self.assertEqual(self.variable.num_unique, 47)

    def test_missing_values(self):
        self.assertEqual(self.variable.missing, '3 (6.00%)')

    def test_graph_plotted(self):
        self.assertIn(b'\x89PNG', self.variable.graphs.getvalue())
