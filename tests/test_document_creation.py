import unittest
from pathlib import Path

import pandas as pd
from docx import Document
from eda_report import get_word_report


class TestDocumentProperties(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame(range(50))
        self.doc_filename = "test-report.docx"

    def test_document_creation(self):
        # Delete the report file if it already exists
        file = Path(self.doc_filename)
        if file.exists():
            file.unlink()
        # Generate the report
        get_word_report(
            self.data, title="Test Report", output_filename=self.doc_filename
        )
        # Check if the report is actually created and saved
        self.assertTrue(Path(self.doc_filename).is_file())
        # Check if the title in the document is as stipulated
        self.assertEqual(
            Document(self.doc_filename).paragraphs[0].text, "Test Report"
        )

    def tearDown(self):
        Path(self.doc_filename).unlink()  # Delete the file
