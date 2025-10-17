import unittest
from typing import List

from importlib.resources import files
from bench.data import DataTable, MdFormat, CsvFormat

class TestTwoWayConversions(unittest.TestCase):

    def _read_test_file(self, name: str) -> str:
        filepath = files("tests.resources").joinpath(name)
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def _test_csv_to_md(self, name):
        csv = self._read_test_file(f"{name}.csv")
        md = self._read_test_file(f"{name}.md")
        self.assertEqual(md.strip('\n'), MdFormat.render(CsvFormat.parse(csv)))

    def _test_md_to_csv(self, name):
        csv = self._read_test_file(f"{name}.csv")
        md = self._read_test_file(f"{name}.md")
        self.assertEqual(csv.strip('\n'), CsvFormat.render(MdFormat.parse(md)))

    def _test_two_way_conv(self, csv, md):
        table = CsvFormat.parse(csv)
        self.assertEqual(md, MdFormat.render(table))
        table = MdFormat.parse(md)
        self.assertEqual(csv, CsvFormat.render(table))

    def test_csv_to_md_samples(self):
        self._test_csv_to_md("sample1")
        self._test_csv_to_md("sample2")
        self._test_csv_to_md("sample3")

    def test_md_to_csv_samples(self):
        self._test_md_to_csv("sample1")
        self._test_md_to_csv("sample2")
        self._test_md_to_csv("sample3")

    def test_simple_conv(self):
        self._test_two_way_conv(
            'Header1,Header2\n'
            'Data1,Data2',
            '| Header1 | Header2 |\n'
            '| ------- | ------- |\n'
            '| Data1   | Data2   |'
        )

    def test_short_or_empty(self):
        self._test_two_way_conv(
            'a,b,c\n'
            ',x,',
            '| a   | b   | c   |\n'
            '| --- | --- | --- |\n'
            '|     | x   |     |'
        )

    def test_header_only(self):
        self._test_two_way_conv(
            'a,b,c',
            '| a   | b   | c   |\n'
            '| --- | --- | --- |'
        )

    def test_quotes_and_commas(self):
        self._test_two_way_conv(
            'Header1,Header2\n'
            '"a,b","a,""b"""',
            '| Header1 | Header2 |\n'
            '| ------- | ------- |\n'
            '| a,b     | a,"b"   |'
        )

    def test_pipes(self):
        self._test_two_way_conv(
            'Header1,Header2\n'
            'a|b,a|b|c',
            '| Header1 | Header2 |\n'
            '| ------- | ------- |\n'
            '| a\\|b    | a\\|b\\|c |'
        )

class TestDataTableConverter(unittest.TestCase):
    def setUp(self):
        self.table = DataTable(["Name", "Age", "Passed"])
        self.table.append(["Alice", 30, True])
        self.table.append(["Bob", 25, False])

    def test_to_csv_lines(self):
        self.assertEqual(CsvFormat.render(self.table),
            "Name,Age,Passed\n"
            "Alice,30,true\n"
            "Bob,25,false"
        )

    def test_csv_round_trip(self):
        new_table = CsvFormat.parse(CsvFormat.render(self.table), parse_types=True)
        self.assertEqual(new_table.cols(), self.table.cols())
        self.assertEqual(new_table.data(), self.table.data())

    def test_to_markdown_lines(self):
        self.assertEqual(MdFormat.render(self.table),
            "| Name  | Age | Passed |\n"
            "| ----- | --- | ------ |\n"
            "| Alice | 30  | true   |\n"
            "| Bob   | 25  | false  |"
        )

    def test_from_markdown_lines(self):
        table = MdFormat.parse(
            "| Name | Age | Passed |\n"
            "| --- | --- | --- |\n"
            "| Charlie | 22 | true |\n"
            "| Dana | 28 | false |\n",
            parse_types=True
        )
        self.assertEqual(table.cols(), ["Name", "Age", "Passed"])
        self.assertEqual(table.data(), [["Charlie", 22, True], ["Dana", 28, False]])

    def test_markdown_round_trip(self):
        new_table = MdFormat.parse(MdFormat.render(self.table), parse_types=True)
        self.assertEqual(new_table.cols(), self.table.cols())
        self.assertEqual(new_table.data(), self.table.data())

if __name__ == "__main__":
    unittest.main()
