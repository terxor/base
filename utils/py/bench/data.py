from typing import List, Optional, Union
from typing import TextIO, Callable
import re
import csv,io

Primitive = Union[bool, int, float, str, type(None)]
Row = Union[dict[str,Primitive], List[Primitive]]

# A `DataTable` is basically ordered tabular data.
# For values, only `Primitive` types are supported.
# However, homogeneity in columns is not mandatory.
# Columns are always stored as strings internally.
# If columns are not provided, a naming convention `f{i}` is used.
class DataTable:

    # Members:
    #   _headers (list of headers)
    #   _header_index (dictionary from label to column index)
    #   _ncols

    def __init__(self, p: Union[int, List[Optional[str]]]):
        if isinstance(p, int):
            if p <= 0:
                raise ValueError("Number of columns must be positive.")
            self._headers = [f"f{i}" for i in range(p)]
        elif isinstance(p, list):
            if len(p) == 0:
                raise ValueError("Number of columns must be positive.")
            for i,c in enumerate(p):
                if not isinstance(c, str):
                    raise ValueError("Each column name must be a string")
            self._headers = list(p)
        else:
            raise ValueError(f"invalid argument for init: {p}")
        
        self._header_index = {}
        for i, h in enumerate(self._headers):
            if h in self._header_index:
                raise ValueError(f"Duplicate column {h}")
            self._header_index[h] = i
        self._ncols = len(self._headers)
        self._data: List[List[Primitive]] = []
        self._nrows = 0

    def size(self) -> int:
        """Returns number of rows"""
        return self._nrows
    
    def cols(self):
        """Returns list of columns"""
        return list(self._headers)
    
    def ncols(self):
        return self._ncols

    def _normalize_row(self, row: Row) -> List[Primitive]:
        if isinstance(row, dict):
            r = [None] * self._ncols
            for k, v in row.items():
                if k in self._header_index:
                    r[self._header_index[k]] = v
            return r
        elif isinstance(row, list):
            if len(row) != self._ncols:
                raise ValueError(f"Row length of {row} does not match number of columns (headers: {self._headers}).")
            for item in row:
                if not isinstance(item, (bool, int, float, str, type(None))):
                    raise TypeError(f"Unsupported data type: {type(item)}")
            return row
        else:
            raise ValueError("invalid argument for row")

    def insert(self, pos: int, row: Row):
        if pos < 0 or pos > self.size():
            raise ValueError("Invalid insert position")
        self._data.insert(pos, self._normalize_row(row)) 
        self._nrows += 1

    def append(self, row: Row):
        self.insert(self.size(), row)

    def index(self, **kwargs) -> int:
        """Find first index of matching params, or -1"""
        vals={}
        for i,h in enumerate(self._headers):
            if h in kwargs:
                vals[i]=kwargs[h]

        for i in range(self.size()):
            match=True
            for index,val in vals.items():
                if self._data[i][index] != val:
                    match=False
                    break
            if match:
                return i
        return -1

    def filter(self, filters: dict[str, Primitive], invert=False) -> "DataTable":
        res = DataTable(self._headers)
        vals={}
        for i,h in enumerate(self._headers):
            if h in filters:
                vals[i]=filters[h]

        for i in range(self.size()):
            match=not invert
            for index,val in vals.items():
                if self._data[i][index] != val:
                    match=invert
                    break
            if match:
                res.append(list(self._data[i]))
        return res
    
    def delete(self, index: int):
        if index < 0 or index >= self.size():
            raise ValueError("Invalid index")
        del self._data[index]
        self._nrows -= 1

    def get(self, index: int) -> dict[str, Primitive]:
        if index < 0 or index >= self.size():
            raise ValueError("Invalid index")
        r={}
        for i in range(self._ncols):
            r[self._headers[i]] = self._data[index][i]
        return r

    def col(self, p: Union[int,str]) -> List[Primitive]:
        if isinstance(p,str):
            index = self._headers.index(p)
        else:
            index = p
        if not isinstance(index, int) or index < 0 or index >= self._ncols:
            raise ValueError("Invalid index")
        res=[]
        for i in range(self.size()):
            res.append(self._data[i][index])
        return res

    def restructure(self, col_map):
        """Returns new table based on column mapping"""
        t = DataTable(list(col_map.keys()))
        indices = []
        for x in col_map.values():
            indices.append(self._headers.index(x))
        for i in range(self.size()):
            r = []
            for j in indices:
                r.append(self._data[i][j])
            t.append(r)
        return t

    def data(self):
        """Returns the internal data as read-only"""
        return [row.copy() for row in self._data]

    def __getitem__(self, index):
        """Allows table[i][j] access via table[i][j] -> table[i][j]"""
        return list(self._data[index])

    def __str__(self):
        """Returns a string representation of the table"""
        output = '\t'.join(self._headers) + '\n'
        for row in self._data:
            output += '\t'.join(str(item) for item in row) + '\n'
        return output.strip()

from abc import ABC, abstractmethod
from typing import List, Union
from bench.data import DataTable

class DataFormat(ABC):
    @staticmethod
    @abstractmethod
    def parse(content: str, **options) -> DataTable:
        pass

    @staticmethod
    @abstractmethod
    def render(table: DataTable, **options) -> str:
        pass

class CsvFormat(DataFormat):
    @staticmethod
    @abstractmethod
    def parse(content: str, **options) -> DataTable:
        parse_types = options.get('parse_types', False)
        trim_spaces = options.get('trim_spaces', False)
        reader = csv.reader(io.StringIO(content))
        header = next(reader)
        header = [f.strip() for f in header]
        table = DataTable(header)
        for row in reader:
            for i,field in enumerate(row):
                if trim_spaces:
                    field = field.strip()
                row[i] = Parser.parse_value(field, parse_types=parse_types)
            table.append(row)
        return table

    @staticmethod
    def render(table: DataTable, **options) -> str:
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL,lineterminator='\n')
        writer.writerow(table.cols())
        for row in table.data():
            row = [Parser._val_to_str(cell) for cell in row]
            writer.writerow(row)

        csv_string = output.getvalue()
        output.close()
        if csv_string[-1] == '\n':
            csv_string = csv_string[:-1]
        return csv_string

# Supported options:
# - color_table: DataTable of equal dimensions as the table
#   to be formatted
# - ignore_header
# - parse_types

class MdFormat(DataFormat):
    @staticmethod
    @abstractmethod
    def parse(content: str, **options) -> DataTable:
        parse_types = options.get('parse_types', False)
        # Supported options:
        # - parse_types, color_table
        lines = content.strip('\n').split('\n')
        if len(lines) == 0:
            raise ValueError("Invalid markdown input")
        header = MdFormat._parse_line(lines[0])
        # line[1] is simply ignored
        table = DataTable(header)
        for line in lines[2:]:
            row = MdFormat._parse_line(line)
            for i, field in enumerate(row):
                row[i] = Parser.parse_value(field, parse_types=parse_types)
            table.append(row)
        return table

    @staticmethod
    def render(table: DataTable, **options) -> str:
        # Options
        ignore_header = options.get('ignore_header', False)
        color_table = options.get('color_table', None)

        # Get headers and data rows from the DataTable object
        headers = table.cols()
        data_rows = table.data()
        num_cols = table.ncols()

        # Calculate max width for each column
        # Initialize with header widths
        col_widths = [max(3, len(header)) for header in headers]

        def val_to_md_str(f):
            res = Parser._val_to_str(f)
            return res.replace('|', r'\|')

        # Precompute stringified rows
        str_rows = [
            [val_to_md_str(cell) for cell in row]
            for row in data_rows
        ]

        # Update widths based on actual data rows
        for row in str_rows:
            for i, cell in enumerate(row):
                # Ensure cell is converted to string for length calculation
                col_widths[i] = max(col_widths[i], len(cell))

        # Helper to pad cells to column width
        def pad(cell: str, width: int, color = None) -> str:
            content = cell
            if color is not None:
                content = TermColor.colorize(cell, color)
            return content + " " * (width - len(cell))

        # Build header row
        header_row = "| " + " | ".join(pad(cell, col_widths[i]) for i, cell in enumerate(headers)) + " |"

        # Build separator row with dashes (left-aligned, matching column width)
        separator_row = "| " + " | ".join("-" * col_widths[i] for i in range(num_cols)) + " |"

        # Build data rows
        lines = [] if ignore_header else [header_row, separator_row]
        for row_idx, row in enumerate(str_rows):
            row_str = "| " + " | ".join(pad(cell, col_widths[i], color_table[row_idx][i] if color_table else None) for i, cell in enumerate(row)) + " |"
            lines.append(row_str)
        return '\n'.join(lines)
    
    @staticmethod
    def _parse_line(line: str) -> List[Optional[str]]:
        """
        Parse one Markdown table row, e.g.:

            "| Alice | 30 | |"`

        → ["Alice", "30", None]
        """
        # 1) Strip leading/trailing pipe and any surrounding spaces
        trimmed = line.strip()
        if trimmed.startswith('|'):
            trimmed = trimmed[1:]
        if trimmed.endswith('|'):
            trimmed = trimmed[:-1]


        # 2) Split using regex that matches unescaped pipes only
        pattern = r'(?<!\\)\|'
        raw_cells = re.split(pattern, trimmed)

        # 3) Replace escaped pipes and strip outer spaces
        def clean(cell: str) -> Optional[str]:
            cell = cell.strip()
            cell = cell.replace(r'\|', '|')
            return cell

        return [clean(cell) for cell in raw_cells]

class Parser:
    @staticmethod
    def parse_value(value: Optional[str], parse_types = True, null_str='') -> Primitive:
        if not parse_types:
            return value or ""
        
        if value is None or not isinstance(value, str) or (null_str is not None and value == null_str):
            return None
        
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        if Parser._is_integer(value):
            return int(value)
        
        if Parser._is_made_of_float_chars(value):
            try:
                return float(value)
            except ValueError:
                pass
        
        return value  # Fallback to string if not boolean, integer, or float

    @staticmethod
    def _is_integer(s: str) -> bool:
        s = s.strip()
        if not s:
            return False
        if s[0] in '+-':
            s = s[1:]
        return s.isdigit()

    @staticmethod
    def _is_made_of_float_chars(s: str) -> bool:
        allowed = {'+', '-', '.', 'e', 'E'}
        return all(c.isdigit() or c in allowed for c in s)

    @staticmethod
    def _val_to_str(val: Primitive) -> str:
        if val is None:
            return ""
        elif isinstance(val, bool):
            return "true" if val else "false"
        elif isinstance(val, float):
            return f"{val:.6g}"
        return str(val)

class TermColor:
    # Class-level color map using ANSI escape codes
    COLOR_MAP = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_black': '\033[90m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
        'reset': '\033[0m',
    }

    @staticmethod
    def colorize(content: str, color = None) -> str:
        """
        Returns the content string wrapped in the given color.
        If color is not found, returns the content unchanged.
        """
        if color is None:
            return content
        color_code = TermColor.COLOR_MAP.get(color.lower())
        reset_code = TermColor.COLOR_MAP['reset']
        if color_code:
            return f"{color_code}{content}{reset_code}"
        else:
            return content  # Fallback if color not found
