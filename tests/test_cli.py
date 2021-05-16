import subprocess
import unittest
from pathlib import Path

import pandas as pd
from docx import Document


class TestCLI(unittest.TestCase):
    def setUp(self):
        # Create a dummy input file
        pd.DataFrame(range(50)).to_csv("test-data.csv")

    def test_command_line_interface(self):
        # Run the program through the command-line interface
        subprocess.run(
            [
                "python",
                "-m",
                "eda_report",
                "test-data.csv",
                "-o",
                "cli-test-report.docx",
                "-t",
                "CLI Test",
            ]
        )
        # Check if a report is generated as specified
        self.assertTrue(Path("cli-test-report.docx").is_file())
        self.assertTrue(
            # Check if the title is as specified
            Document("cli-test-report.docx").paragraphs[0].text,
            "CLI Test",
        )

    def tearDown(self):
        for filename in {"test-data.csv", "cli-test-report.docx"}:
            Path(filename).unlink(missing_ok=True)  # Delete the file
