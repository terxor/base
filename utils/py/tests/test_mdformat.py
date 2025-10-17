import unittest
from bench.data import MdFormat

class TestMdParsing(unittest.TestCase):

    def test_null_values_md(self):
        table = MdFormat.parse( 
            '| f0   | f1   | f2   |\n'
            '| ---- | ---- | ---- |\n'
            '|      |      |      |\n'
        )
        self.assertEqual(table.size(), 1)
        self.assertEqual(table.cols(), ['f0','f1','f2'])
        self.assertEqual(table[0], ['','',''])

    def test_null_values_md_parse_types(self):
        # Empty strings are parsed as None
        table = MdFormat.parse( 
            '| f0   | f1   | f2   |\n'
            '| ---- | ---- | ---- |\n'
            '|      |      |      |\n',
            parse_types=True
        )
        self.assertEqual(table.size(), 1)
        self.assertEqual(table.cols(), ['f0','f1','f2'])
        self.assertEqual(table[0], [None,None,None])

    def test_parsing_simple(self):
        table = MdFormat.parse( 
            ' |u|v| \n' # Header determines ncols (here 2) for each row
            '\n'
            '|a|1|\n'
            '|b|2|\n',
            parse_types=True
        )
        self.assertEqual(table.size(), 2)
        self.assertEqual(table.cols(), ['u','v'])
        self.assertEqual(table.data(), [['a',1],['b',2]])

    def test_col_mismatch(self):
        with self.assertRaises(ValueError):
            table = MdFormat.parse( 
                ' |u|v| \n' # Header determines ncols (here 2) for each row
                '\n'
                '|a|\n'
                '|b|2|\n',
                parse_types=True
            )

    def test_uncommon_cases_md(self):
        table = MdFormat.parse(
            '| 1 | 2 |\n'
            '|---|---|\n'
            '| "" |  xyz |\n'
            '| "    " |   |\n'
            '| "    " | |\n'
            '| | |\n'
            '| a long sentence | with a \\| pipe inside quotes |\n'
            '| | "  fully quoted" |\n'
            '| true | True |\n'
            '| TRUE | false |\n'
            '| 0  | 0.5 |\n',
            parse_types=True
        )
        self.assertEqual(table.size(), 9)
        self.assertEqual(table.cols(), ['1', '2'])
        expected_rows = [
            ['""', 'xyz'],
            ['"    "', None],
            ['"    "', None],
            [None, None],
            ['a long sentence', 'with a | pipe inside quotes'],
            [None, '"  fully quoted"'],
            [True, True],
            [True, False],
            [0, 0.5],
        ]
        self.assertEqual(table.data(), expected_rows)

    def test_more_weird_quote_cases_md(self):
        # No quoting considerations in MD, we parse it as it is.
        table = MdFormat.parse(
            '| col1 | col2 | col3 |\n'
            '|------|------|------|\n'
            '|   "ab""c""d"   | """""x"""""   | "" x "" y "" |\n'
            '| quotes at " random " places | " " | """ |\n'
            '| quotes at "" random "" places |   |   |\n'
            '| ","","""," | | |\n',
            parse_types=True
        )
        self.assertEqual(table.size(), 4)
        self.assertEqual(table.cols(), ['col1', 'col2', 'col3'])
        expected_rows = [
            ['"ab""c""d"', '"""""x"""""', '"" x "" y ""'],
            ['quotes at " random " places', '" "', '"""'],
            ['quotes at "" random "" places', None, None],
            ['","",""","', None, None],
        ]
        self.assertEqual(table.data(), expected_rows)


class TestMdFormatting(unittest.TestCase):

    def test_md_formatting(self):
        self.assertEqual(MdFormat.render(MdFormat.parse(
            '| col1 |col2| col3 |\n'
            '|------|------|------|\n'
            '|1| 2     | 3|\n'
            '| 4    | 5 | "6" |\n'
            '| 7 | "8" | 9 |\n'
            )),
            '| col1 | col2 | col3 |\n'
            '| ---- | ---- | ---- |\n'
            '| 1    | 2    | 3    |\n'
            '| 4    | 5    | "6"  |\n'
            '| 7    | "8"  | 9    |'
        )

    def test_md_formatting_numeric_reformat(self):
        self.assertEqual(MdFormat.render(MdFormat.parse(
            '| col1 | col2 | col3 |\n'
            '|------|------|------|\n'
            '| +1.0 | -2e3 | 3.14 |\n'
            '| 0040 | -3.666666667 | 0.0000000000000001 |\n',
            parse_types=True)),
            '| col1 | col2     | col3  |\n'
            '| ---- | -------- | ----- |\n'
            '| 1    | -2000    | 3.14  |\n'
            '| 40   | -3.66667 | 1e-16 |'
        )

if __name__ == "__main__":
    unittest.main()
