#!/usr/bin/python3

import sqlite3
from bench.data import DataTable
from enum import Enum
from typing import List, Optional

import sqlite3
from typing import Dict, List

class InMemoryDb:
    def __init__(self, tables: Dict[str, DataTable]):
        self._conn = sqlite3.connect(':memory:')
        self._cursor = self._conn.cursor()
        self._create_tables(tables)

    def _create_tables(self, tables: Dict[str, DataTable]):
        for table_name, table in tables.items():
            types = [t.name for t in TypeInferer.infer(table)]

            columns = [f'"{name}" {col_type}' for name, col_type in zip(table.cols(), types)]
            create_stmt = f'CREATE TABLE "{table_name}" ({", ".join(columns)});'
            self._cursor.execute(create_stmt)

            # Insert data
            placeholders = ', '.join('?' * table.ncols())
            insert_stmt = f'INSERT INTO "{table_name}" VALUES ({placeholders});'
            for row in table.data():
                self._cursor.execute(insert_stmt, row)
        
        self._conn.commit()

    def query(self, sql: str) -> DataTable:
        self._cursor.execute(sql)
        headers = [desc[0] for desc in self._cursor.description]
        rows = self._cursor.fetchall()

        result = DataTable(headers)
        for row in rows:
            result.append(list(row))
        return result

    def close(self):
        self._conn.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass  # Prevent exceptions during garbage collection

class SQLiteType(Enum):
    INTEGER = 1
    REAL = 2
    TEXT = 3

class TypeInferer:
    promotion_rules = {
        (None, SQLiteType.INTEGER): SQLiteType.INTEGER,
        (None, SQLiteType.REAL): SQLiteType.REAL,
        (None, SQLiteType.TEXT): SQLiteType.TEXT,

        (SQLiteType.INTEGER, SQLiteType.INTEGER): SQLiteType.INTEGER,
        (SQLiteType.INTEGER, SQLiteType.REAL): SQLiteType.REAL,
        (SQLiteType.INTEGER, SQLiteType.TEXT): SQLiteType.TEXT,

        (SQLiteType.REAL, SQLiteType.INTEGER): SQLiteType.REAL,
        (SQLiteType.REAL, SQLiteType.REAL): SQLiteType.REAL,
        (SQLiteType.REAL, SQLiteType.TEXT): SQLiteType.TEXT,

        (SQLiteType.TEXT, SQLiteType.INTEGER): SQLiteType.TEXT,
        (SQLiteType.TEXT, SQLiteType.REAL): SQLiteType.TEXT,
        (SQLiteType.TEXT, SQLiteType.TEXT): SQLiteType.TEXT,
    }

    @staticmethod
    def value_to_type(value) -> SQLiteType:
        if isinstance(value, str):
            return SQLiteType.TEXT
        elif isinstance(value, float):
            return SQLiteType.REAL
        elif isinstance(value, int):  # includes bool
            return SQLiteType.INTEGER
        else:
            return SQLiteType.TEXT  # fallback

    @classmethod
    def promote(cls, current: Optional[SQLiteType], value_type: SQLiteType) -> SQLiteType:
        return cls.promotion_rules.get((current, value_type), SQLiteType.TEXT)

    @classmethod
    def infer(cls, table) -> List[SQLiteType]:
        inferred: List[Optional[SQLiteType]] = [None] * table.ncols()

        for row in table.data():
            for i, value in enumerate(row):
                val_type = cls.value_to_type(value)
                inferred[i] = cls.promote(inferred[i], val_type)

        return [t if t is not None else SQLiteType.TEXT for t in inferred]

# Convenience method for querying of a single DataTable
# The table is referred by default name 't'
def quick_query (table: DataTable, query: str) -> DataTable:
    return InMemoryDb({'t': table}).query(query)

