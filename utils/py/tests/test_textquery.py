import unittest
from bench.data import DataTable
from bench.textquery import InMemoryDb, TypeInferer, SQLiteType, quick_query

class TestInMemoryDb(unittest.TestCase):

    def setUp(self):
        # People table
        self.people = DataTable(["Name", "Age", "IsStudent"])
        self.people.append(["Alice", 30, True])
        self.people.append(["Bob", 25, False])
        self.people.append(["Charlie", 35, True])

        # Courses table
        self.courses = DataTable(["CourseID", "CourseName"])
        self.courses.append([101, "Mathematics"])
        self.courses.append([102, "Physics"])
        self.courses.append([103, "Literature"])

        # Enrollments table (many-to-many relationship)
        self.enrollments = DataTable(["Name", "CourseID"])
        self.enrollments.append(["Alice", 101])
        self.enrollments.append(["Alice", 102])
        self.enrollments.append(["Charlie", 103])

        # Initialize in-memory DB with all tables
        self.db = InMemoryDb({
            "people": self.people,
            "courses": self.courses,
            "enrollments": self.enrollments
        })


    def tearDown(self):
        self.db.close()

    def test_query_all(self):
        result = self.db.query("SELECT * FROM people")
        self.assertEqual(result.size(), 3)
        self.assertEqual(result.ncols(), 3)
        self.assertEqual(result.cols(), ["Name", "Age", "IsStudent"])
        expected_rows = [
            ["Alice", 30, 1],
            ["Bob", 25, 0],
            ["Charlie", 35, 1]
        ]
        self.assertEqual(result.data(), expected_rows)

    def test_query_filter(self):
        result = self.db.query("SELECT Name FROM people WHERE Age > 30")
        self.assertEqual(result.size(), 1)
        self.assertEqual(result.ncols(), 1)
        self.assertEqual(result.cols(), ["Name"])
        self.assertEqual(result.data(), [["Charlie"]])

    def test_query_count(self):
        result = self.db.query("SELECT COUNT(*) FROM people WHERE IsStudent = 1")
        self.assertEqual(result.size(), 1)
        self.assertEqual(result.ncols(), 1)
        self.assertEqual(result.cols(), ["COUNT(*)"])
        self.assertEqual(result.data(), [[2]])

    def test_query_projection(self):
        result = self.db.query("SELECT Name, IsStudent FROM people")
        self.assertEqual(result.size(), 3)
        self.assertEqual(result.ncols(), 2)
        self.assertEqual(result.cols(), ["Name", "IsStudent"])
        expected_rows = [
            ["Alice", 1],
            ["Bob", 0],
            ["Charlie", 1]
        ]
        self.assertEqual(result.data(), expected_rows)

    def test_empty_result(self):
        result = self.db.query("SELECT * FROM people WHERE Age < 10")
        self.assertEqual(result.size(), 0)
        self.assertEqual(result.cols(), ["Name", "Age", "IsStudent"])
        self.assertEqual(result.data(), [])

    def test_people_course_join(self):
        result = self.db.query("""
            SELECT people.Name, courses.CourseName
            FROM people
            JOIN enrollments ON people.Name = enrollments.Name
            JOIN courses ON enrollments.CourseID = courses.CourseID
        """)

        self.assertEqual(result.cols(), ["Name", "CourseName"])
        self.assertEqual(result.size(), 3)

        expected_rows = [
            ["Alice", "Mathematics"],
            ["Alice", "Physics"],
            ["Charlie", "Literature"]
        ]

        actual_rows = sorted(result.data())  # sort for comparison
        expected_rows = sorted(expected_rows)

        self.assertEqual(actual_rows, expected_rows)


class TestTypeInferer(unittest.TestCase):
    def test_all_integer(self):
        table = DataTable(["ID", "Age"])
        table.append([1, 30])
        table.append([2, 40])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.INTEGER, SQLiteType.INTEGER])

    def test_mixed_real_integer(self):
        table = DataTable(["Score"])
        table.append([95])
        table.append([82.5])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.REAL])

    def test_mixed_with_text(self):
        table = DataTable(["Info"])
        table.append(["abc"])
        table.append([123])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.TEXT])

    def test_empty_table(self):
        table = DataTable(["A", "B"])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.TEXT, SQLiteType.TEXT])

    def test_boolean_handling(self):
        table = DataTable(["Active"])
        table.append([True])
        table.append([False])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.INTEGER])

    def test_schema_inference(self):
        table = DataTable(["Name", "Age", "IsStudent"])
        table.append(["Alice", 30, True])
        table.append(["Bob", 25, False])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.TEXT, SQLiteType.INTEGER, SQLiteType.INTEGER])

class TestQuickQuery(unittest.TestCase):

    def test_quick_query_works(self):
        table = DataTable(["Name", "Age", "IsStudent"])
        table.append(["Alice", 30, True])
        table.append(["Bob", 25, False])
        result = quick_query(table, "select Age as a from t")
        self.assertEqual(result.size(), 2)
        self.assertEqual(result.ncols(), 1)
        self.assertEqual(result.cols(), ["a"])
        self.assertEqual(result.data(), [[30],[25]])

if __name__ == '__main__':
    unittest.main()
