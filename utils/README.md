# utils: General utilities

## `dfx` - Data Format eXchange

To transform data from one format to another. This is meant for plaintext,
lightweight usage.

Two formats are supported:

- CSV
- Markdown tabular format

### Examples

Input file `infile`:

```
key,value
a,5
b,6
c,7
```

Command:

```
dfx --from csv --to md < infile
```

Output:

```
| key | value |
| --- | ----- |
| a   | 5     |
| b   | 6     |
| c   | 7     |
```

Transformation from MD to CSV, naturally, is also possible.

One can use the following command to reformat a MD table:

```
dfx --from md --to md
```

Conversions including type parsing are also possible
using the `--parse-types` flag, for example:

Input file `infile`:

```
key,value
a,5.000
b,6e2
c,7
```

Output:

```
dfx --from csv --to md --parse-types < infile
| key | value |
| --- | ----- |
| a   | 5     |
| b   | 600   |
| c   | 7     |
```

A feature particularly for terminals, and only supported for markdown
format is colors. One can specify output colors by a series of rules
of form `[<row range>][<col range>]=<color>`, for example:

```
dfx --from csv --to md --parse-types --md-colors "[2:][]=red,[3][2]=green" < $tb/a
```

Would effectively color rows 2 to end as red (all columns), then overwrite
cell 3,2 with color green.

Other flags:

- `--md-no-header`: Do not print header (first 2 lines) in md format
- `--tf-backtick`: Accepts list of 1-index comma separated columns and adds a
  surrounds the contents by backticks. Useful for markdown representation.

--------------------------------------------------------------------------------

## `textquery` - SQL on plaintext data

### `quick_query`: Single table query (for python usage)

```py
from bench.data import DataTable, MdFormat
from bench.textquery import quick_query

table = DataTable(['name', 'count'])
table.append(['a', 1])
table.append(['a', 2])
table.append(['b', 3])
table.append(['b', 4])

result = quick_query(table, "select name, sum(count) as sum from t group by name")
print(MdFormat.render(result))

# | name | sum |
# | ---- | --- |
# | a    | 3   |
# | b    | 7   |
```

--------------------------------------------------------------------------------

## `timestamp` - Standard timestamps from flexible input

Simply running `timestamp` gives the current time in different forms:

```
| Category | Type     | Value                      |
| -------- | -------- | -------------------------- |
| epoch    | seconds  | 1759912626                 |
| epoch    | ms       | 1759912626012              |
| epoch    | micros   | 1759912626012673           |
| UTC      | standard | 2025-10-08 08:37:06        |
| UTC      | micros   | 2025-10-08 08:37:06.012673 |
| UTC      | iso      | 2025-10-08T08:37:06+0000   |
| IST      | standard | 2025-10-08 14:07:06        |
| IST      | micros   | 2025-10-08 14:07:06.012673 |
| IST      | iso      | 2025-10-08T14:07:06+0530   |
| PST      | standard | 2025-10-08 01:37:06        |
| PST      | micros   | 2025-10-08 01:37:06.012673 |
| PST      | iso      | 2025-10-08T01:37:06-0700   |
```

The command accepts flexible forms, for example:

- `timestamp 2000` : Equivalent to `2000-01-01 00:00:00`
- `timestamp 2000-01` : Month
- `timestamp 2000-01-01` : Date
- `timestamp '2000-01-01 00:00:00'` : Timestamp
- `timestamp 1750000000` : Epoch seconds
- `timestamp 1750000000000` : Epoch millis
- `timestamp 1750000000000000` : Epoch micros

--------------------------------------------------------------------------------

## `tmpbuf` - Temporary Buffers

A thin layer (and a convention) to manage temporary buffers, which allows you to
type and think slightly lesser to access such files.

First set environment variable `tb` to a directory of your choice.
`tmpbuf` or `tb` will then provide a more convenient access to
files `a-z` and `0-9` in the directory. Files `0-9` are executable files.

```
tb        # Open first empty buffer in editor
tb a      # Open buffer `a` in editor
tb -i     # Regenerate the files
tb -l     # List contents of all used buffers in a summarized form
tb -u     # Open all used buffers in editor
tb -f     # Prints all free buffers in a line
```

The standard way to access these files also works (through env var `$tb`):

```
vim $tb/a
cat $tb/a
my_command > $tb/b
$tb/1   # Directly execute
rm $tb/[a-z] # Clear all
```

--------------------------------------------------------------------------------
