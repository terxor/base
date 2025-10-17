import pytz
from datetime import datetime, timezone
from typing import Dict, Tuple
from typing import Optional

from bench.data import DataTable

class TimeOutput:
    def __init__(self, dt: datetime, tz_map: Dict[str, str]):
        """
        dt: tz-aware datetime (ideally UTC)
        tz_list: list of timezone labels to output, e.g. ['UTC', 'IST', 'PST']
        tz_map: dict mapping labels to pytz timezone names, e.g. {'IST': 'Asia/Kolkata'}
        """
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise ValueError("datetime object must be timezone-aware")

        # Normalize to UTC
        dt_utc = dt.astimezone(pytz.UTC)

        timestamp = dt_utc.timestamp()
        self.epoch_seconds = int(timestamp)
        self.epoch_millis = int(timestamp * 1_000)
        self.epoch_micros = int(timestamp * 1_000_000)

        self.tz_times: Dict[str, Tuple[str, str, str]] = {}

        fmt_lambdas = [
                lambda d: ('standard', d.strftime("%Y-%m-%d %H:%M:%S")),
                lambda d: ('micros', d.strftime("%Y-%m-%d %H:%M:%S.%f")),
                lambda d: ('iso', d.strftime("%Y-%m-%dT%H:%M:%S%z")),
        ]
        self.num_fmt = len(fmt_lambdas)
        self.fmt_names = [f(dt_utc)[0] for f in fmt_lambdas]

        for key, pytz_name in tz_map.items():
            tz = pytz.timezone(pytz_name)
            dt_tz = dt_utc.astimezone(tz)

            self.tz_times[key] = [f(dt_tz)[1] for f in fmt_lambdas]

    def __repr__(self):
        return (
            f"TimeOutput(epoch_seconds={self.epoch_seconds}, "
            f"epoch_millis={self.epoch_millis}, epoch_micros={self.epoch_micros}, "
            f"tz_times={self.tz_times})"
        )

    def __eq__(self, other):
        if not isinstance(other, TimeOutput):
            return False
        return (
            self.epoch_seconds == other.epoch_seconds and
            self.epoch_millis == other.epoch_millis and
            self.epoch_micros == other.epoch_micros and
            self.tz_times == other.tz_times
        )

class TimeParser:
    """
    A utility class for parsing various time string formats and epoch timestamps
    into timezone-aware datetime objects.
    """

    # Default timezone label to assume for naive inputs
    DEFAULT_TZ = 'UTC'

    # Mapping of friendly labels to pytz timezone names
    LABEL_TO_PYTZ = {
        DEFAULT_TZ: DEFAULT_TZ,
        'IST': 'Asia/Kolkata',
        'PST': 'America/Los_Angeles'
    }

    # Acceptable input datetime string formats
    DATETIME_INPUT_FORMATS = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z", # Handles timezone information if present
    ]

    @staticmethod
    def _detect_epoch_precision(value: float) -> datetime:
        """
        Detects the precision of an epoch timestamp (seconds, millis, micros, nanos)
        and converts it to a UTC datetime object.

        Args:
            value: The epoch timestamp as a float or int.

        Returns:
            A timezone-aware datetime object in UTC.

        Raises:
            ValueError: If the epoch timestamp is too small to be considered valid.
        """
        MIN_VALID_EPOCH = 10000000 # Roughly corresponds to 1970-04-26

        if value < MIN_VALID_EPOCH:
            raise ValueError("Epoch timestamp too small to be valid. Did you mean a year?")

        if value < 1e12:
            return datetime.fromtimestamp(value, tz=timezone.utc)  # seconds
        elif value < 1e15:
            return datetime.fromtimestamp(value / 1e3, tz=timezone.utc)  # milliseconds
        elif value < 1e18:
            return datetime.fromtimestamp(value / 1e6, tz=timezone.utc)  # microseconds
        else:
            # Fallback for nanoseconds if it's an extremely large number
            return datetime.fromtimestamp(value / 1e9, tz=timezone.utc)  # nanoseconds

    @staticmethod
    def parse_time_string(value: str) -> datetime:
        """
        Parses a datetime string into a naive or timezone-aware datetime object.
        This function prioritizes detailed formats and falls back to partial date formats.

        Args:
            value: The datetime string to parse.

        Returns:
            A datetime object, which might be naive if no timezone info is present
            in the string and no explicit timezone is applied.

        Raises:
            ValueError: If the datetime string cannot be parsed by any known format.
        """
        # Try detailed datetime formats first (including those with %z for timezone)
        for fmt in TimeParser.DATETIME_INPUT_FORMATS:
            try:
                dt = datetime.strptime(value, fmt)
                return dt
            except ValueError:
                continue

        # Fallback for partial dates (e.g., "2023-10-27", "2023-10", "2023")
        fallback_formats = [
            ("%Y-%m-%d", "%Y-%m-%d 00:00:00"),
            ("%Y-%m", "%Y-%m-01 00:00:00"),
            ("%Y", "%Y-01-01 00:00:00"),
        ]
        for test_fmt, full_fmt_str in fallback_formats:
            try:
                # Parse the partial string to get the base date
                parsed_partial_dt = datetime.strptime(value, test_fmt)
                # Format this base date into a full datetime string with default time
                full_dt_str = parsed_partial_dt.strftime(full_fmt_str)
                # Then parse the full datetime string
                padded_dt = datetime.strptime(full_dt_str, "%Y-%m-%d %H:%M:%S")
                return padded_dt
            except ValueError:
                continue

        raise ValueError(f"Could not parse datetime input: '{value}'.")

    @staticmethod
    def parse(time_input: Optional[str] = None, source_tz_label: Optional[str] = None) -> datetime:
        """
        Parses a time string (or uses current time) and a timezone label to return
        a timezone-aware datetime object.

        Args:
            time_input: The input string. Can be an epoch timestamp (e.g., "1678886400"),
                        a datetime string (e.g., "2023-10-27 10:30:00"), or None for current time.
            source_tz_label: The friendly label for the timezone to assume if the time_input
                             is a naive datetime string (e.g., 'IST', 'PST'). Defaults to 'UTC'.

        Returns:
            A timezone-aware datetime object representing the parsed time.

        Raises:
            ValueError: If the time_input cannot be parsed or the source_tz_label is unknown.
            pytz.UnknownTimeZoneError: If the resolved pytz timezone name is invalid.
        """
        # If no input, return current time localized to the specified/default timezone
        if time_input is None:
            resolved_tz_label = source_tz_label if source_tz_label else TimeParser.DEFAULT_TZ
            if resolved_tz_label not in TimeParser.LABEL_TO_PYTZ:
                 raise ValueError(f"Unknown timezone label: '{resolved_tz_label}' for current time.")
            
            pytz_tz_name = TimeParser.LABEL_TO_PYTZ[resolved_tz_label]
            try:
                target_tz = pytz.timezone(pytz_tz_name)
                return datetime.now(target_tz)
            except pytz.UnknownTimeZoneError:
                raise ValueError(f"Invalid pytz timezone name derived from label '{resolved_tz_label}': '{pytz_tz_name}'.")

        # Attempt to parse as epoch timestamp
        try:
            epoch_value = float(time_input)
            return TimeParser._detect_epoch_precision(epoch_value) # This returns UTC aware datetime
        except ValueError:
            # Not an epoch, proceed to datetime string parsing
            pass

        # Attempt to parse as a datetime string
        dt = TimeParser.parse_time_string(time_input)

        # If the parsed datetime is naive, localize it using source_tz_label
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            resolved_tz_label = source_tz_label if source_tz_label else TimeParser.DEFAULT_TZ
            if resolved_tz_label not in TimeParser.LABEL_TO_PYTZ:
                raise ValueError(f"Unknown timezone label: '{resolved_tz_label}'.")
            
            pytz_tz_name = TimeParser.LABEL_TO_PYTZ[resolved_tz_label]
            try:
                target_tz = pytz.timezone(pytz_tz_name)
                # Localize the naive datetime object
                dt = target_tz.localize(dt)
            except pytz.UnknownTimeZoneError:
                raise ValueError(f"Invalid pytz timezone name derived from label '{resolved_tz_label}': '{pytz_tz_name}'.")
        
        return dt


def convert_time_output_to_data_table(time_output: TimeOutput) -> DataTable:
    """
    Converts a TimeOutput object into a DataTable for structured display.

    Args:
        time_output: An instance of the TimeOutput class containing time data.

    Returns:
        A DataTable instance populated with the time output information.
    """
    
    # Define table headers and number of columns based on the desired output format
    headers = ['Category', 'Type', 'Value']
    num_columns = len(headers)
    
    # Initialize the DataTable
    data_table = DataTable(headers)

    # Add Epoch time rows
    data_table.append(['epoch', 'seconds', time_output.epoch_seconds])
    data_table.append(['epoch', 'ms', time_output.epoch_millis])
    data_table.append(['epoch', 'micros', time_output.epoch_micros])

    # Add Timezone specific time rows
    for label in time_output.tz_times.keys():
        for i in range(time_output.num_fmt):
            category = label
            time_type = time_output.fmt_names[i]
            value = time_output.tz_times[label][i]
            data_table.append([category, time_type, value])
            
    return data_table

def parse_time (
    time_input: Optional[str] = None,
    source_tz_label: Optional[str] = None
) -> TimeOutput:
    """
    Parses a time string or epoch timestamp and returns a TimeOutput object.

    Args:
        time_input: The input string (epoch timestamp or datetime string).
        source_tz_label: The timezone label to assume for naive datetime strings.

    Returns:
        A TimeOutput object containing parsed time information in various formats.

    Raises:
        ValueError: If the input cannot be parsed or the timezone label is unknown.
    """
    dt = TimeParser.parse(time_input, source_tz_label)
    tz_map = TimeParser.LABEL_TO_PYTZ
    return TimeOutput(dt, tz_map)
