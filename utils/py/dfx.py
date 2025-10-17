#!/usr/bin/python3

import sys
import argparse
from bench.data import CsvFormat, MdFormat

def main():
    parser = argparse.ArgumentParser(description="Convert CSV to markdown")
    parser.add_argument('input_file', nargs='?', type=argparse.FileType('r', encoding='utf-8'),
                        default=sys.stdin,
                        help="Input Markdown file (default: stdin)")
    parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout, help="Output CSV file (default: stdout)")

    allowed_values = ['md', 'csv']
    parser.add_argument(
        '--from',
        dest='from_format',
        choices=allowed_values,
        required=True,
        help="Source format"
    )

    parser.add_argument(
        '--to',
        dest='to_format',
        choices=allowed_values,
        required=True,
        help="Target format"
    )

    parser.add_argument(
        '--parse-types',
        action='store_true',
        help="Whether to parse types (e.g. double, int) during transformation"
    )

    # Additional transforms while conversion
    parser.add_argument(
        '--tf-backtick',
        dest='transform_backtick',
        type=str,
        default=None,
        help="Comma sep list of 1-indexed cols to toggle backtick on"
    )

    # Additional transforms while conversion
    parser.add_argument(
        '--md-colors',
        dest='md_colors',
        type=str,
        default=None,
        help="""
Apply terminal colors to markdown output.
The format is a bit complex to allow a lot of custom coloring.
For example: "[2:][1]=red,[][2]=green,[2][1]=blue" would mean
- Color all rows with indices >= 2 in column 1 as red
- Color all rows in column 2 as green
- Color row 2 in column 1 as blue

Rules are applied in the given order
"""
    )

    parser.add_argument(
        '--md-no-header',
        dest='md_no_header',
        action='store_true',
        help="Whether to not print header for MD table"
    )

    parser.add_argument(
        '--csv-preserve-spaces',
        dest='csv_preserve_spaces',
        action='store_true',
        help="Whether to preserve spaces. Default is trim."
    )

    args = parser.parse_args()
    content=args.input_file.read()
    if args.from_format == 'csv':
      table = CsvFormat.parse(content, parse_types=args.parse_types, trim_spaces=(not args.csv_preserve_spaces))
    elif args.from_format == 'md':
      table = MdFormat.parse(content, parse_types=args.parse_types)
    else:
      raise ValueError(f"Unsupported format: {args.from_format}")

    # TODO: Refactor to modularize data transforms
    if args.transform_backtick:
      cols = [int(x) - 1 for x in args.transform_backtick.split(',')]
      (nrows, _) = table.size()
      for i in range(nrows):
          for c in cols:
            val = table[i][c]
            if val is None:
               continue
            val = str(val)
            if val.startswith("`") and val.endswith("`"):
              res = val[1:-1]
            else:
              res = f'`{val}`'
            table[i][c] = res

    color_table=None
    if args.md_colors:
        color_table = parse_and_generate_color_table(args.md_colors, table.size(), table.ncols())

    output = ''
    if args.to_format == 'md':
        output = MdFormat.render(table, color_table=color_table, ignore_header=args.md_no_header)
    elif args.to_format == 'csv':
        output = CsvFormat.render(table)
    else:
      raise ValueError(f"Unsupported format: {args.to_format}")
    print(output)

def parse_and_generate_color_table(rule_str, n_rows, n_cols):
    """
    Parse a color rules string and generate a concrete color table.

    Args:
        rule_str: string from CLI, e.g., "[2:][1]=red,[][2]=green,[2][1]=blue"
        n_rows: number of data rows (excluding header)
        n_cols: number of columns

    Returns:
        2D list [n_rows][n_cols] of color strings or None
    """
    # ---- parse rules ----
    import re
    if not rule_str.strip():
        return [[None]*n_cols for _ in range(n_rows)]

    rule_pattern = re.compile(r'^\[(.*?)\]\[(.*?)\]=(.*)$')
    rules = []
    for raw_rule in rule_str.split(","):
        raw_rule = raw_rule.strip()
        if not raw_rule:
            continue
        m = rule_pattern.match(raw_rule)
        if not m:
            raise ValueError(f"Invalid rule format: {raw_rule}")
        row_sel, col_sel, color = m.groups()

        def parse_selector(sel):
            sel = sel.strip()
            if sel == "":
                return None
            if ":" in sel:
                parts = sel.split(":")
                start = int(parts[0]) if parts[0] else None
                end = int(parts[1]) if len(parts) > 1 and parts[1] else None
                return (start, end)
            else:
                n = int(sel)
                return (n, n)

        row_range = parse_selector(row_sel)
        col_range = parse_selector(col_sel)
        rules.append({"row": row_range, "col": col_range, "color": color.strip()})

    # ---- generate color table ----
    table = [[None for _ in range(n_cols)] for _ in range(n_rows)]

    def in_range(idx, rng):
        if rng is None:
            return True
        start, end = rng
        if start is not None and idx < start:
            return False
        if end is not None and idx > end:
            return False
        return True

    for rule in rules:
        for r in range(1, n_rows+1):
            for c in range(1, n_cols+1):
                if in_range(r, rule["row"]) and in_range(c, rule["col"]):
                    table[r-1][c-1] = rule["color"]

    return table

if __name__ == "__main__":
    main()

