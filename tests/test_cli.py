import unittest
from pathlib import Path

import pandas as pd
from eda_report.cli import process_cli_args


class TestCLIArgumentParsing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a dummy input file
        pd.DataFrame(range(50)).to_csv("test-data.csv", index=False)

    @classmethod
    def tearDownClass(cls):
        Path("test-data.csv").unlink()  # Delete the dummy file

    def test_with_all_args(self):
        args = process_cli_args(
            "test-data.csv",
            "-o",
            "cli-test-1.docx",
            "-t",
            "CLI Test",
            "-c",
            "teal",
            "-T",
            "0",
        )
        # Check whether the supplied arguments were set
        self.assertIsInstance(args.infile, pd.DataFrame)
        self.assertEqual(args.outfile, "cli-test-1.docx")
        self.assertEqual(args.title, "CLI Test")
        self.assertEqual(args.color, "teal")
        self.assertEqual(args.target, "0")

    def test_with_default_args(self):
        args = process_cli_args("test-data.csv")
        # Check if the default arguments were set
        self.assertIsInstance(args.infile, pd.DataFrame)
        self.assertEqual(args.outfile, "eda-report.docx")
        self.assertEqual(args.title, "Exploratory Data Analysis Report")
        self.assertEqual(args.color, "orangered")
        self.assertEqual(args.target, None)
