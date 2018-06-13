import tempfile
from unittest import TestCase

import pandas as pd

from pyutil.excel.excel import Excel, excelBook


class TestExcel(TestCase):
    def test_excel(self):
        e = Excel()
        self.assertIsNotNone(e.book)
        e.add_frame(frame=pd.DataFrame(index=["A"], columns=["AA"], data=[[1]]), sheetname="Peter")
        # you can either use the name of a file
        e.to_file(file=tempfile.NamedTemporaryFile(delete=True).name)
        # or the file directly
        e.to_file(file=tempfile.NamedTemporaryFile(delete=True))

    def test_excel_book(self):
        e = excelBook(title="Peter", subject="Maffay")
        self.assertIsNotNone(e)
        self.assertIsNotNone(e.format_number)
        self.assertIsNotNone(e.format_percent)
        self.assertIsInstance(e, Excel)