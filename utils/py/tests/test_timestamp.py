import unittest
import time

from bench.timestamp import TimeOutput, TimeParser, convert_time_output_to_data_table, parse_time

class TestTimestampParsing(unittest.TestCase):
    def test_day_parse(self):
        output = parse_time('2025-01-01')
        self.assertEqual(output.epoch_seconds, 1735689600)
        self.assertEqual(output.epoch_millis, 1735689600000)
        self.assertEqual(output.epoch_micros, 1735689600000000)

        self.assertIn('UTC', output.tz_times)
        self.assertIn('IST', output.tz_times)
        self.assertIn('PST', output.tz_times)

        for label in ['UTC', 'IST', 'PST']:
            formats = output.tz_times[label]
            self.assertEqual(len(formats), 3)  # ISO, human-readable, microseconds

        self.assertEqual(output.tz_times['UTC'][0], '2025-01-01 00:00:00')
        self.assertEqual(output.tz_times['UTC'][1], '2025-01-01 00:00:00.000000')
        self.assertEqual(output.tz_times['UTC'][2], '2025-01-01T00:00:00+0000')

        self.assertEqual(output.tz_times['IST'][0], '2025-01-01 05:30:00')
        self.assertEqual(output.tz_times['IST'][1], '2025-01-01 05:30:00.000000')
        self.assertEqual(output.tz_times['IST'][2], '2025-01-01T05:30:00+0530')

        self.assertEqual(output.tz_times['PST'][0], '2024-12-31 16:00:00')
        self.assertEqual(output.tz_times['PST'][1], '2024-12-31 16:00:00.000000')
        self.assertEqual(output.tz_times['PST'][2], '2024-12-31T16:00:00-0800')

    def test_timestamp_parse(self):
        output = parse_time('2025-05-26 02:10:51', 'PST')
        self.assertEqual(output.epoch_seconds, 1748250651)
        self.assertEqual(output.epoch_millis, 1748250651000)
        self.assertEqual(output.epoch_micros, 1748250651000000)

        self.assertIn('UTC', output.tz_times)
        self.assertIn('IST', output.tz_times)
        self.assertIn('PST', output.tz_times)

        for label in ['UTC', 'IST', 'PST']:
            formats = output.tz_times[label]
            self.assertEqual(len(formats), 3)  # ISO, human-readable, microseconds

        self.assertEqual(output.tz_times['UTC'][0], '2025-05-26 09:10:51')
        self.assertEqual(output.tz_times['UTC'][1], '2025-05-26 09:10:51.000000')
        self.assertEqual(output.tz_times['UTC'][2], '2025-05-26T09:10:51+0000')

        self.assertEqual(output.tz_times['IST'][0], '2025-05-26 14:40:51')
        self.assertEqual(output.tz_times['IST'][1], '2025-05-26 14:40:51.000000')
        self.assertEqual(output.tz_times['IST'][2], '2025-05-26T14:40:51+0530')

        self.assertEqual(output.tz_times['PST'][0], '2025-05-26 02:10:51')
        self.assertEqual(output.tz_times['PST'][1], '2025-05-26 02:10:51.000000')
        self.assertEqual(output.tz_times['PST'][2], '2025-05-26T02:10:51-0700')

    def test_us_parse(self):
        output = parse_time('1735689612987654')
        self.assertEqual(output.epoch_seconds, 1735689612)
        self.assertEqual(output.epoch_millis, 1735689612987)
        self.assertEqual(output.epoch_micros, 1735689612987654)

        self.assertIn('UTC', output.tz_times)
        self.assertIn('IST', output.tz_times)
        self.assertIn('PST', output.tz_times)

        for label in ['UTC', 'IST', 'PST']:
            formats = output.tz_times[label]
            self.assertEqual(len(formats), 3)  # ISO, human-readable, microseconds

        self.assertEqual(output.tz_times['UTC'][0], '2025-01-01 00:00:12')
        self.assertEqual(output.tz_times['UTC'][1], '2025-01-01 00:00:12.987654')
        self.assertEqual(output.tz_times['UTC'][2], '2025-01-01T00:00:12+0000')

        self.assertEqual(output.tz_times['IST'][0], '2025-01-01 05:30:12')
        self.assertEqual(output.tz_times['IST'][1], '2025-01-01 05:30:12.987654')
        self.assertEqual(output.tz_times['IST'][2], '2025-01-01T05:30:12+0530')

        self.assertEqual(output.tz_times['PST'][0], '2024-12-31 16:00:12')
        self.assertEqual(output.tz_times['PST'][1], '2024-12-31 16:00:12.987654')
        self.assertEqual(output.tz_times['PST'][2], '2024-12-31T16:00:12-0800')

    def test_equality(self):
        self.assertEqual(
                parse_time('2025-01-01'),
                parse_time('1735689600')
        )
        self.assertEqual(
                parse_time('2025-01-01'),
                parse_time('2025-01')
        )
        self.assertEqual(
                parse_time('2025-01-01'),
                parse_time('2025')
        )

    def test_equality_zones(self):
        self.assertEqual(
                parse_time('2025-05-26 15:00:00', 'IST'),
                parse_time('2025-05-26 02:30:00', 'PST')
        )

    def test_no_args(self):
        now_output = parse_time()
        now_output_exp = parse_time(str(time.time()))
        # at least seconds should be equal
        self.assertEqual(
                now_output.epoch_seconds,
                now_output_exp.epoch_seconds
        )

    def test_convert_to_datatable(self):
        table = convert_time_output_to_data_table(parse_time('2025-05-26 02:10:51', 'PST'))
        self.assertEqual(table.cols(), ['Category','Type','Value'])
        self.assertEqual(table.data(),
            [['epoch', 'seconds', 1748250651],
             ['epoch', 'ms', 1748250651000],
             ['epoch', 'micros', 1748250651000000],
             ['UTC', 'standard', '2025-05-26 09:10:51'],
             ['UTC', 'micros', '2025-05-26 09:10:51.000000'],
             ['UTC', 'iso', '2025-05-26T09:10:51+0000'],
             ['IST', 'standard', '2025-05-26 14:40:51'],
             ['IST', 'micros', '2025-05-26 14:40:51.000000'],
             ['IST', 'iso', '2025-05-26T14:40:51+0530'],
             ['PST', 'standard', '2025-05-26 02:10:51'],
             ['PST', 'micros', '2025-05-26 02:10:51.000000'],
             ['PST', 'iso', '2025-05-26T02:10:51-0700']]
        )

if __name__ == "__main__":
    unittest.main()

