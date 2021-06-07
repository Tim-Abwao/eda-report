import unittest
from pathlib import Path

import pandas as pd
from docx import Document
from eda_report import get_word_report
import seaborn as sns


class TestDocumentProperties(unittest.TestCase):
    def setUp(self):
        self.doc_filename = "test-report.docx"

    def test_report_for_multivariate_mixed_type_dataset(self):
        get_word_report(
            data=sns.load_dataset("iris"),
            output_filename=self.doc_filename,
            title="Mutlivariate",
        )
        # Check if the report is actually created and saved
        self.assertTrue(Path(self.doc_filename).is_file())
        # Check if the title in the document is as stipulated
        self.assertEqual(
            Document(self.doc_filename).paragraphs[0].text, "Mutlivariate"
        )

    def test_report_for_numeric_univariate_data(self):
        # Generate the report
        get_word_report(
            data=pd.DataFrame(range(50)),
            output_filename=self.doc_filename,
            title="Numeric Univariate",
        )
        # Check if the report is actually created and saved
        self.assertTrue(Path(self.doc_filename).is_file())
        # Check if the title in the document is as stipulated
        self.assertEqual(
            Document(self.doc_filename).paragraphs[0].text,
            "Numeric Univariate",
        )

    def test_report_for_categorical_univariate_data(self):
        # Generate the report
        get_word_report(
            data=pd.DataFrame(["only one item"]),
            output_filename=self.doc_filename,
            title="Categorical Univariate",
        )
        # Check if the report is actually created and saved
        self.assertTrue(Path(self.doc_filename).is_file())
        # Check if the title in the document is as stipulated
        self.assertEqual(
            Document(self.doc_filename).paragraphs[0].text,
            "Categorical Univariate",
        )

    def tearDown(self):
        Path(self.doc_filename).unlink()  # Delete the file
