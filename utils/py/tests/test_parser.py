import unittest
from bench.data import Parser

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_none_value(self):
        self.assertIsNone(self.parser.parse_value(None))

    def test_empty_string(self):
        self.assertEqual(self.parser.parse_value(""), None)
        self.assertEqual(self.parser.parse_value("",null_str=None), "")

    def test_boolean_true(self):
        self.assertIs(self.parser.parse_value("true"), True)
        self.assertIs(self.parser.parse_value("True"), True)
        self.assertIs(self.parser.parse_value("TRUE"), True)

    def test_boolean_false(self):
        self.assertIs(self.parser.parse_value("false"), False)
        self.assertIs(self.parser.parse_value("False"), False)
        self.assertIs(self.parser.parse_value("FALSE"), False)

    def test_integer(self):
        self.assertEqual(self.parser.parse_value("0"), 0)
        self.assertEqual(self.parser.parse_value("00"), 0)
        self.assertEqual(self.parser.parse_value("42"), 42)
        self.assertEqual(self.parser.parse_value("-100"), -100)
    
    def test_integer_variants(self):
        self.assertEqual(self.parser.parse_value("0"), 0)
        self.assertEqual(self.parser.parse_value("-0"), 0)
        self.assertEqual(self.parser.parse_value("123"), 123)
        self.assertEqual(self.parser.parse_value("-456"), -456)
        self.assertEqual(self.parser.parse_value("+789"), 789)
        self.assertEqual(self.parser.parse_value("0000123"), 123)

    def test_float(self):
        self.assertEqual(self.parser.parse_value("3.14"), 3.14)
        self.assertEqual(self.parser.parse_value("-0.01"), -0.01)
        self.assertEqual(self.parser.parse_value(".5"), 0.5)
        self.assertEqual(self.parser.parse_value("2e3"), 2000.0)
        self.assertEqual(self.parser.parse_value("-1.5E-2"), -0.015)
    
    def test_float_variants(self):
        self.assertEqual(self.parser.parse_value("3.0"), 3.0)
        self.assertEqual(self.parser.parse_value("0.0"), 0.0)
        self.assertEqual(self.parser.parse_value("-0.0"), -0.0)
        self.assertEqual(self.parser.parse_value("+3.5"), 3.5)
        self.assertEqual(self.parser.parse_value(".5"), 0.5)
        self.assertEqual(self.parser.parse_value("5."), 5.0)
        self.assertEqual(self.parser.parse_value("-.75"), -0.75)
        self.assertEqual(self.parser.parse_value("1e2"), 100.0)
        self.assertEqual(self.parser.parse_value("1E2"), 100.0)
        self.assertEqual(self.parser.parse_value("-2e-3"), -0.002)
        self.assertEqual(self.parser.parse_value("6.02E23"), 6.02e23)
        self.assertEqual(self.parser.parse_value("+1.5e+3"), 1500.0)
        self.assertEqual(self.parser.parse_value("0e0"), 0.0)

    def test_string_fallback(self):
        self.assertEqual(self.parser.parse_value("hello"), "hello")
        self.assertEqual(self.parser.parse_value("123abc"), "123abc")
        self.assertEqual(self.parser.parse_value(" "), " ")

if __name__ == "__main__":
    unittest.main()
