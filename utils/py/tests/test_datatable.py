import unittest

from bench.data import DataTable

class TestDataTable(unittest.TestCase):
    def test_initialization_with_headers(self):
        table = DataTable(["Name", "Age"])
        self.assertEqual(table.cols(), ["Name", "Age"])
        self.assertEqual(table.ncols(), 2)
        self.assertEqual(table.size(), 0)

    def test_initialization_with_default_headers(self):
        table = DataTable(3)
        self.assertEqual(table.cols(), ['f0', 'f1', 'f2'])

    def test_invalid_column_number(self):
        with self.assertRaises(ValueError):
            DataTable(0)

    def test_unique_headers(self):
        with self.assertRaises(ValueError):
            DataTable(["a", "a"])

    def test_add_valid_row(self):
        table = DataTable(2)
        table.append(["Alice", 25])
        self.assertEqual(table.size(), 1)
        self.assertEqual(table[0][0], "Alice")
        self.assertEqual(table[0][1], 25)

    def test_add_partial_row(self):
        table = DataTable(2)
        table.append({"f0": "a", "f1": 1})
        table.append({"f1": 2})
        self.assertEqual(table.size(), 2)
        self.assertEqual(table[0], ["a", 1])
        self.assertEqual(table[1], [None, 2])

    def test_insert(self):
        table = DataTable(1)
        table.append(["a"])
        table.insert(0, ["b"])
        table.insert(2, ["c"])
        self.assertEqual(table.size(), 3)
        self.assertEqual(table.col(0), ["b","a","c"])

    def test_add_invalid_row_length(self):
        table = DataTable(2)
        with self.assertRaises(ValueError):
            table.append(["Only one item"])

    def test_add_invalid_data_type(self):
        table = DataTable(1)
        with self.assertRaises(TypeError):
            table.append([{"name": "Alice"}])  # dict is not allowed

    def test_str_output(self):
        table = DataTable(["Col1", "Col2"])
        table.append([1, 2.5])
        table.append(["Text", True])
        expected = "Col1\tCol2\n1\t2.5\nText\tTrue"
        self.assertEqual(str(table), expected)

    def test_col(self):
        table = DataTable(2)
        table.append(["a",1])
        table.append(["b",2])
        table.append(["c",3])
        self.assertEqual(table.col(0), ["a","b","c"])
        self.assertEqual(table.col("f1"), [1,2,3])

    def test_get(self):
        table = DataTable(["Col1", "Col2"])
        table.append([1, 2.5])
        table.append(["Text", True])
        self.assertEqual(table.get(0), {"Col1": 1, "Col2": 2.5})
        self.assertEqual(table[0], [1, 2.5])
        self.assertEqual(table.get(1), {"Col1": "Text", "Col2": True})
        self.assertEqual(table[1], ["Text", True])

    def test_find_index(self):
        table = DataTable(2)
        table.append(["a",1])
        table.append(["b",2])
        table.append(["b",4])
        table.append(["c",3])
        self.assertEqual(table.size(), 4)
        self.assertEqual(table.index(f0="b"), 1)

    def test_filter(self):
        table = DataTable(2)
        table.append(["a",1])
        table.append(["b",2])
        table.append(["b",4])
        table.append(["c",3])
        filtered = table.filter(filters={"f0":"b"})

        self.assertEqual(table.size(), 4)
        self.assertEqual(filtered.size(), 2)
        self.assertEqual(filtered.cols(), table.cols())
        self.assertEqual(filtered.data(), [["b",2],["b",4]])

    def test_filter_invert(self):
        table = DataTable(2)
        table.append(["a",1])
        table.append(["b",2])
        table.append(["b",4])
        table.append(["c",3])
        filtered = table.filter(filters={"f0":"b"}, invert=True)

        self.assertEqual(table.size(), 4)
        self.assertEqual(filtered.size(), 2)
        self.assertEqual(filtered.cols(), table.cols())
        self.assertEqual(filtered.data(), [["a",1],["c",3]])

    def test_delete(self):
        table = DataTable(2)
        table.append(["a",1])
        table.append(["b",2])
        table.append(["c",3])
        self.assertEqual(table.size(), 3)
        table.delete(1)
        self.assertEqual(table.size(), 2)
        self.assertEqual(table.col(0), ["a","c"])

    def test_restructure(self):
        table = DataTable(3)
        table.append(["a",1,True])
        table.append(["b",2,False])
        table.append(["c",3,True])
        table2 = table.restructure({"id": "f1", "name": "f0"});
        self.assertEqual(table.size(), 3)
        self.assertEqual(table.cols(), ["f0","f1","f2"])
        self.assertEqual(table2.size(), 3)
        self.assertEqual(table2.cols(), ["id","name"])
        self.assertEqual(table2.col(0), [1,2,3])
        self.assertEqual(table2.col(1), ["a","b","c"])

if __name__ == '__main__':
    unittest.main()
