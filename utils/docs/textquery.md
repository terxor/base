## Text query examples

| ID | Name       | Category   | Value | Status   |
|----|------------|------------|-------|----------|
| 1  | Alpha      | Type A     | 23.5  | Active   |
| 2  | Bravo      | Type B     | 15.0  | Inactive |
| 3  | Charlie    | Type C     | 18.2  | Active   |
| 4  | Delta      | Type A     | 21.9  | Pending  |
| 5  | Echo       | Type B     | 16.7  | Active   |
| 6  | Foxtrot    | Type C     | 19.4  | Inactive |
| 7  | Golf       | Type A     | 20.1  | Active   |
| 8  | Hotel      | Type B     | 22.8  | Pending  |
| 9  | India      | Type C     | 17.3  | Active   |
| 10 | Juliett    | Type A     | 24.0  | Inactive |


```
select * from t where Status = 'Active'
```

| ID  | Name    | Category | Value | Status |
| --- | ------- | -------- | ----- | ------ |
| 1   | Alpha   | Type A   | 23.5  | Active |
| 3   | Charlie | Type C   | 18.2  | Active |
| 5   | Echo    | Type B   | 16.7  | Active |
| 7   | Golf    | Type A   | 20.1  | Active |
| 9   | India   | Type C   | 17.3  | Active |

```
select Category, avg(Value) from t group by Category
```

| Category | avg(Value)         |
| -------- | ------------------ |
| Type A   | 22.375             |
| Type B   | 18.166666666666668 |
| Type C   | 18.3               |


| timestamp           | value |
| ------------------- | ----- |
| 2025-06-11 19:53:31 | 1     |
| 2025-06-11 19:54:31 | 2     |
| 2025-06-11 19:56:31 | 5     |
| 2025-06-11 20:00:31 | 9     |

```
select strftime('%s', timestamp) as timestamp, value from t
```

| timestamp  | value |
| ---------- | ----- |
| 1749671611 | 1     |
| 1749671671 | 2     |
| 1749671791 | 5     |
| 1749672031 | 9     |

```
select * from (
  select *,
  (timestamp - lag(timestamp) over ()) as t_delta,
  (value - lag(value) over ()) as v_delta
  from t
) where t_delta is not null and v_delta is not null
```

| timestamp  | value | t_delta | v_delta |
| ---------- | ----- | ------- | ------- |
| 1749671671 | 2     | 60      | 1       |
| 1749671791 | 5     | 120     | 3       |
| 1749672031 | 9     | 240     | 4       |

********************************************************************************

| ID  | Name    | Category | Value | IsActive |
| --- | ------- | -------- | ----- | -------- |
| 1   | Alpha   | Type A   | 23.5  | true     |
| 2   | Bravo   | Type B   | 15.0  | false    |
| 3   | Charlie | Type C   | 18.2  | true     |
| 4   | Delta   | Type A   | 21.9  | false    |
| 5   | Echo    | Type B   | 16.7  | false    |
| 6   | Foxtrot | Type C   | 19.4  | false    |
| 7   | Golf    | Type A   | 20.1  | true     |
| 8   | Hotel   | Type B   | 22.8  | false    |
| 9   | India   | Type C   | 17.3  | true     |
| 10  | Juliett | Type A   | 24.0  | true     |

```
pragma table_info(T)
```

| cid | name     | type    | notnull | dflt_value | pk  |
| --- | -------- | ------- | ------- | ---------- | --- |
| 0   | ID       | INTEGER | 0       |            | 0   |
| 1   | Name     | TEXT    | 0       |            | 0   |
| 2   | Category | TEXT    | 0       |            | 0   |
| 3   | Value    | REAL    | 0       |            | 0   |
| 4   | IsActive | INTEGER | 0       |            | 0   |

