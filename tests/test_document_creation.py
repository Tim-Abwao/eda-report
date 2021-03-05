
import pandas as pd
import os
import unittest
from docx import Document
from eda_report import get_word_report


class TestDocumentProperties(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame(range(50))
        self.doc_filename = 'test-report.docx'

    def test_document_creation(self):
        if os.path.isfile(self.doc_filename):
            os.remove(self.doc_filename)
        get_word_report(self.data, title='Test Report',
                        output_filename=self.doc_filename)
        # Check if the report is actually created and saved
        self.assertTrue(os.path.isfile(self.doc_filename))
        # Check if the title in the document is as stipulated
        self.assertEqual(
            Document(self.doc_filename).paragraphs[0].text,
            'Test Report'
        )

    def tearDown(self):
        if os.path.isfile(self.doc_filename):
            os.remove(self.doc_filename)
