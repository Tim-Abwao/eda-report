import unittest

import pandas as pd
from eda_report.univariate import Variable


class TestGeneralVariableProperties(unittest.TestCase):

    def setUp(self):
        some_sample = pd.Series(range(50), name='some variable')
        some_sample.iloc[[0, 10, 20]] = None  # Introduce missing values
        self.variable = Variable(some_sample)
        self.nameless_variable = Variable(pd.Series(range(50)))
        self.named_variable = Variable(pd.Series(range(50)), name='any name')

    def test_variable_name(self):
        # Check if the variable's name is captured
        self.assertEqual(self.variable.name, 'some variable')
        self.assertIsNone(self.nameless_variable.name)
        self.assertEqual(self.named_variable.name, 'any name')

    def test_unique_values(self):
        # Check if unique values are correctly captured
        self.assertEqual(self.variable.num_unique, 47)

    def test_missing_values(self):
        # Check if missing values are correctly captured
        self.assertEqual(self.variable.missing, '3 (6.00%)')


class TestNumericVariables(unittest.TestCase):

    def setUp(self):
        self.variable = Variable(
            pd.Series(range(50), name='numbers')
        )

    def test_data_type(self):
        # Check if data type is numeric
        self.assertEqual(self.variable.var_type, 'numeric')

    def test_summary_statistics_present(self):
        # Check if all summary statistics are present
        self.assertEqual(
            self.variable.statistics.index.to_list(),
            ['Number of observations', 'Average', 'Standard Deviation',
             'Minimum', 'Lower Quartile', 'Median', 'Upper Quartile',
             'Maximum', 'Skewness', 'Kurtosis']
        )

    def test_summary_statistics_values(self):
        # Check if summary statistics values are consistent
        self.assertAlmostEqual(
            self.variable.statistics.loc['Number of observations', 'numbers'],
            50)
        self.assertAlmostEqual(
            self.variable.statistics.loc['Average', 'numbers'], 24.5)
        self.assertAlmostEqual(
            self.variable.statistics.loc['Standard Deviation', 'numbers'],
            14.5773797)
        self.assertAlmostEqual(
            self.variable.statistics.loc['Minimum', 'numbers'], 0)
        self.assertAlmostEqual(
            self.variable.statistics.loc['Lower Quartile', 'numbers'], 12.25)
        self.assertAlmostEqual(
            self.variable.statistics.loc['Median', 'numbers'], 24.5)
        self.assertAlmostEqual(
            self.variable.statistics.loc['Upper Quartile', 'numbers'], 36.75)
        self.assertAlmostEqual(
            self.variable.statistics.loc['Maximum', 'numbers'], 49)
        self.assertAlmostEqual(
            self.variable.statistics.loc['Skewness', 'numbers'], 0)
        self.assertAlmostEqual(
            self.variable.statistics.loc['Kurtosis', 'numbers'], -1.2)

    def test_graph_plotted(self):
        self.assertEqual(
            ['hist_and_boxplot', 'qq_plot', 'run_plot'], 
            list(self.variable._graphs)
        )
        self.assertIn(
            b'\x89PNG', self.variable._graphs['hist_and_boxplot'].getvalue())
        self.assertIn(
            b'\x89PNG', self.variable._graphs['qq_plot'].getvalue())
        self.assertIn(
            b'\x89PNG', self.variable._graphs['run_plot'].getvalue())


class TestCategoricalVariables(unittest.TestCase):

    def setUp(self):
        self.variable = Variable(
            pd.Series(['a']*15 + ['b']*25 + ['c']*10, name='letters')
        )
        self.variable_from_bool = Variable(
            pd.Series([True, False] * 25, name='bool')
        )

    def test_data_type(self):
        # Check if data type is categorical
        self.assertEqual(self.variable.var_type, 'categorical')
        self.assertEqual(self.variable_from_bool.var_type, 'categorical')

    def test_summary_statistics_present(self):
        # Check if all summary statistics are present
        self.assertEqual(
            self.variable.statistics.index.to_list(),
            ['Number of observations', 'Unique values',
             'Mode (Highest occurring value)']
        )

    def test_summary_statistics_values(self):
        # Check if summary statistics values are consistent
        self.assertAlmostEqual(
            self.variable.statistics.loc['Number of observations', 'letters'],
            50)
        self.assertAlmostEqual(
            self.variable.statistics.loc['Unique values', 'letters'], 3)
        self.assertAlmostEqual(
            self.variable.statistics.loc[
                'Mode (Highest occurring value)', 'letters'
            ], 'b'
        )

    def test_most_common_values(self):
        # Check if the most common values are correctly captured
        self.assertEqual(
            self.variable.most_common_items['letters'].to_list(),
            ['25 (50.00%)', '15 (30.00%)', '10 (20.00%)']
        )
        self.assertEqual(
            self.variable.most_common_items.index.to_list(),
            ['b', 'a', 'c']
        )

    def test_graph_plotted(self):
        self.assertIn(
            'bar_plot', self.variable._graphs
        )
        self.assertIn(
            b'\x89PNG', self.variable._graphs['bar_plot'].getvalue()
        )
