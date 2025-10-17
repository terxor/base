
TODO:

Testing:

Run unit tests from this directory only:

```
py -m unittest discover -s tests -p 'test_*.py' -v

# or
py -m unittest -v tests/test_*.py
```

Python library usage example:

```py
from bench.data import DataTable, MdFormat

table = DataTable(3, ['id', 'name', 'comment'])
table.add_row([1, 'abc', 'First comment'])
table.add_row([2, 'pqr', 'Second comment'])

lines = MdFormat(table).format(colors=['red','green','blue'])
print(*lines, sep='\n')
```
