import unittest
from bench.data import CsvFormat

class TestCsvParsing(unittest.TestCase):

    def test_from_csv_lines(self):
        table = CsvFormat.parse(
            "Name,Age,Passed\n"
            "Charlie,22,true\n"
            "Dana,28,false\n"
        )
        self.assertEqual(table.cols(), ["Name", "Age", "Passed"])
        self.assertEqual(table.data(), [["Charlie", "22", "true"], ["Dana", "28", "false"]])

    def test_from_csv_lines_parse_types(self):
        table = CsvFormat.parse(
            "Name,Age,Passed\n"
            "Charlie,22,true\n"
            "Dana,28,false\n",
            parse_types=True
        )
        self.assertEqual(table.cols(), ["Name", "Age", "Passed"])
        self.assertEqual(table.data(), [["Charlie", 22, True], ["Dana", 28, False]])

    def test_null_values(self):
        table = CsvFormat.parse(
            "a,b,c\n"
            ",,\n",
            parse_types=True
        )
        self.assertEqual(table.size(), 1)
        self.assertEqual(table.cols(), ['a','b','c'])
        self.assertEqual(table.data(), [[None, None, None]])

    def test_uncommon_cases_csv(self):
        table = CsvFormat.parse(
            '1,2\n' # Even though columns are seemingly ints, they are treated as strings
            '"",  xyz\n' # Initial empty spaces are trimmed.
            '"    ",   \n' # Both are strings, second is null effectively
            '"    ",\n' # In this case, the second column is null
            ',\n' # Both are null
            'a long sentence   ,"with a comma, inside quotes"\n' # Leading and trailing spaces are trimmed, comma inside quotes is preserved
            ',"  fully quoted"\n'
            'true,True\n'
            'TRUE,false\n'
            '0  , 0.5\n'
            'ab""efg,""cd""\n' # Note that [""cd""] is malformed, but we still parse it as ["cd"]
            '"x""abc""","""cd"""\n', # ["""cd"""] is okay - parsed as ["cd"]
            parse_types=True,
        )
        self.assertEqual(table.size(), 11)
        self.assertEqual(table.cols(), ['1', '2'])
        expected_rows = [
            [None, '  xyz'], # Empty strings are treated as null
            ['    ', '   '],
            ['    ', None],
            [None, None],
            ['a long sentence   ', 'with a comma, inside quotes'],
            [None, '  fully quoted'],
            [True, True],
            [True, False],
            [0, ' 0.5'],
            ['ab""efg', 'cd""'],
            ['x"abc"', '"cd"'],
        ]
        self.assertEqual(table.data(), expected_rows)

    def test_uncommon_cases_trim_spaces_csv(self):
        table = CsvFormat.parse(
            '1,2\n' # Even though columns are seemingly ints, they are treated as strings
            '"",  xyz\n' # Initial empty spaces are trimmed.
            '"    ",   \n' # Both are strings, second is null effectively
            '"    ",\n' # In this case, the second column is null
            ',\n' # Both are null
            'a long sentence   ,"with a comma, inside quotes"\n' # Leading and trailing spaces are trimmed, comma inside quotes is preserved
            ',"  fully quoted"\n'
            'true,True\n'
            'TRUE,false\n'
            '0  , 0.5\n'
            'ab""efg,""cd""\n' # Note that [""cd""] is malformed, but we still parse it as ["cd"]
            '"x""abc""","""cd"""\n', # ["""cd"""] is okay - parsed as ["cd"]
            parse_types=True,
            trim_spaces=True
        )
        self.assertEqual(table.size(), 11)
        self.assertEqual(table.cols(), ['1', '2'])
        expected_rows = [
            [None, 'xyz'],
            [None, None],
            [None, None],
            [None, None],
            ['a long sentence', 'with a comma, inside quotes'],
            [None, 'fully quoted'],
            [True, True],
            [True, False],
            [0, 0.5],
            ['ab""efg', 'cd""'],
            ['x"abc"', '"cd"'],
        ]
        self.assertEqual(table.data(), expected_rows)

    def test_more_weird_quote_cases(self):
        table = CsvFormat.parse(
            'a,b,c\n'
            '   "ab""c""d"   , """""x"""""   , "" x "" y "" \n' # Leading spaces cause exact parsing
            'here is a " string " with quotes at " random " places," ",""""\n' # stray quotes are just parsed as they are
            '"here is a "" string "" with quotes at "" random "" places",   ,   \n' # quotes only need to be escaed when whole string is quoted
            '","",""",,\n', # Look closely at the first part
            parse_types=True
        )
        self.assertEqual(table.size(), 4)
        self.assertEqual(table.cols(), ['a','b','c'])
        expected_rows = [
            ['   "ab""c""d"   ',' """""x"""""   ',' "" x "" y "" '],
            ['here is a " string " with quotes at " random " places', ' ', '"'],
            ['here is a " string " with quotes at " random " places', '   ', '   '],
            [',","', None, None],
        ]
        self.assertEqual(table.data(), expected_rows)

class TestCsvFormatting(unittest.TestCase):

    def test_csv_formatting(self):
        self.assertEqual(
            CsvFormat.render(CsvFormat.parse(
                'col1 ,col2,  col3\n'
                '  1 ,    2  ,3\n'
                ' 4,5,"6"\n'
                '7,"8",9   \n',
                trim_spaces=True
            )),
            'col1,col2,col3\n'
            '1,2,3\n'
            '4,5,6\n'
            '7,8,9'
        )

    def test_csv_formatting_numeric_reformat(self):
        self.assertEqual(
            CsvFormat.render(CsvFormat.parse(
                ' a , b , c  \n'
                '+1.0,-2e3,3.14\n'
                '0040,-3.666666667,0.0000000000000001\n',
                parse_types=True
            )),
            'a,b,c\n'
            '1,-2000,3.14\n'
            '40,-3.66667,1e-16'
        )

if __name__ == "__main__":
    unittest.main()

