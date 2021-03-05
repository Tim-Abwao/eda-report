import subprocess
import pandas as pd
import os
import unittest
from docx import Document


class TestCLI(unittest.TestCase):

    def setUp(self):
        pd.DataFrame(range(50)).to_csv('test-data.csv')

    def test_command_line_interface(self):
        # Run the package
        subprocess.run(
            ['python', '-m', 'eda_report', 'test-data.csv', '-o',
             'cli-test-report.docx', '-t', 'CLI Test']
        )
        self.assertTrue(os.path.isfile('cli-test-report.docx'))
        self.assertTrue(
            Document('cli-test-report.docx').paragraphs[0].text,
            'CLI Test'
        )

    def tearDown(self):
        for file in {'test-data.csv', 'cli-test-report.docx'}:
            if os.path.isfile(file):
                os.remove(file)
