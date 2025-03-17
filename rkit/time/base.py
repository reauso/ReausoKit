import sys
from copy import deepcopy
from enum import StrEnum, auto
from functools import cached_property, lru_cache
from re import Match, compile
from typing import Union, Any, Self, Pattern
from bidict import frozenbidict

from rkit.list import list_quotient, list_product
from rkit.patterns import Singleton


class TimeUnit(StrEnum):
    """
    Enumeration representing various time units.
    """
    NANOSECOND = auto()
    MICROSECOND = auto()
    MILLISECOND = auto()
    SECOND = auto()
    MINUTE = auto()
    HOUR = auto()
    DAY = auto()
    WEEK = auto()

    @classmethod
    @lru_cache
    def symbols(cls) -> frozenbidict[Self, str]:
        return frozenbidict({
            cls.NANOSECOND: 'ns',
            cls.MICROSECOND: 'μs',
            cls.MILLISECOND: 'ms',
            cls.SECOND: 's',
            cls.MINUTE: 'm',
            cls.HOUR: 'h',
            cls.DAY: 'd',
            cls.WEEK: 'w',
        })

    @classmethod
    @lru_cache
    def unofficial_symbol_map(cls) -> frozenbidict[str, Self]:
        return frozenbidict({
            'us': cls.MICROSECOND,
        })

    @classmethod
    @lru_cache(10)
    def _missing_(cls, key) -> Self:
        if not isinstance(key, str):
            return None

        if key.upper() in cls._member_map_:
            return cls._member_map_[key.upper()]

        if key in cls.symbols().inverse:
            return cls.symbols().inverse[key]

        if key in cls.unofficial_symbol_map():
            return cls.unofficial_symbol_map()[key]

        return None

    @classmethod
    def ordered_ascending(cls) -> tuple['TimeUnit', ...]:
        return (
            TimeUnit.NANOSECOND,
            TimeUnit.MICROSECOND,
            TimeUnit.MILLISECOND,
            TimeUnit.SECOND,
            TimeUnit.MINUTE,
            TimeUnit.HOUR,
            TimeUnit.DAY,
            TimeUnit.WEEK,
        )

    @cached_property
    def symbol(self) -> str:
        return self.symbols()[self]

    @property
    def greater_units_ascending(self) -> tuple['TimeUnit', ...]:
        units = self.ordered_ascending()
        idx = units.index(self)
        return units[idx + 1:]

    @property
    def smaller_units_descending(self) -> tuple['TimeUnit', ...]:
        units = self.ordered_ascending()
        idx = units.index(self)
        return units[max(idx - 1, 0)::-1]


@Singleton
class TimeUnitConversionTable:
    """
    Singleton class for managing time unit conversions.
    """

    # This must be sorted!
    _supported_units = [
        TimeUnit.NANOSECOND,
        TimeUnit.MICROSECOND,
        TimeUnit.MILLISECOND,
        TimeUnit.SECOND,
        TimeUnit.MINUTE,
        TimeUnit.HOUR,
        TimeUnit.DAY,
        TimeUnit.WEEK,
    ]

    def __init__(self) -> None:
        """
        Initializes the conversion table by computing transition factors
        between supported time units.
        """
        transition_factors = [1000.0, 1000.0, 1000.0, 60.0, 60.0, 24.0, 7.0]
        self._transition_table: dict[TimeUnit, dict[TimeUnit, float]] = {}

        for from_idx, from_unit in enumerate(self._supported_units):
            self._transition_table[from_unit] = {}

            for to_idx, to_unit in enumerate(self._supported_units):
                if from_idx < to_idx:
                    factor = list_quotient(transition_factors[from_idx:to_idx])
                elif from_idx > to_idx:
                    factor = list_product(transition_factors[to_idx:from_idx])
                else:
                    factor = 1.0

                self._transition_table[from_unit][to_unit] = factor

    def factor(self, from_unit: TimeUnit, to_unit: TimeUnit) -> float:
        """
        Retrieves the conversion factor between two time units.

        :param from_unit: The original time unit.
        :param to_unit: The target time unit.
        :return: The conversion factor (for multiplication).
        """
        return self._transition_table[from_unit][to_unit]


TimeUnitConversionTable()


class Timedelta:
    """
    A class representing a duration of time with precision down to nanoseconds.

    This class supports arithmetic operations, conversions, and
    formatted string representation.
    """

    SUPPORTED_UNITS = {
        TimeUnit.NANOSECOND,
        TimeUnit.MICROSECOND,
        TimeUnit.MILLISECOND,
        TimeUnit.SECOND,
        TimeUnit.MINUTE,
        TimeUnit.HOUR,
        TimeUnit.DAY,
        TimeUnit.WEEK,
    }
    _unit_conversion_table = TimeUnitConversionTable.safe_instance
    _total_time_function_map = {
        TimeUnit.NANOSECOND: lambda self: self.total_nanoseconds,
        TimeUnit.MICROSECOND: lambda self: self.total_microseconds,
        TimeUnit.MILLISECOND: lambda self: self.total_milliseconds,
        TimeUnit.SECOND: lambda self: self.total_seconds,
        TimeUnit.MINUTE: lambda self: self.total_minutes,
        TimeUnit.HOUR: lambda self: self.total_hours,
        TimeUnit.DAY: lambda self: self.total_days,
        TimeUnit.WEEK: lambda self: self.total_weeks,
    }
    _portion_time_function_map = {
        TimeUnit.NANOSECOND: lambda self: self.nanoseconds_portion,
        TimeUnit.MICROSECOND: lambda self: self.microseconds_portion,
        TimeUnit.MILLISECOND: lambda self: self.milliseconds_portion,
        TimeUnit.SECOND: lambda self: self.seconds_portion,
        TimeUnit.MINUTE: lambda self: self.minutes_portion,
        TimeUnit.HOUR: lambda self: self.hours_portion,
        TimeUnit.DAY: lambda self: self.days_portion,
        TimeUnit.WEEK: lambda self: self.weeks_portion,
    }

    @classmethod
    def supports_unit(cls, unit: TimeUnit) -> bool:
        return unit in cls.SUPPORTED_UNITS

    @classmethod
    @lru_cache
    def supported_time_symbols(cls) -> set[str]:
        return (
            {unit.symbol for unit in cls.SUPPORTED_UNITS}
            | {symbol for symbol, unit in TimeUnit.unofficial_symbol_map().items() if unit in cls.SUPPORTED_UNITS}
        )

    @classmethod
    @lru_cache
    def _format_spec_regex(cls) -> Pattern:
        return compile(
        r"(?P<all>\{(?P<unit>"
        rf"{'|'.join(cls.supported_time_symbols())}"
        r"+)(?P<spec>:[^}]*)?\})"
    )

    @classmethod
    def min(cls) -> 'Timedelta':
        """Returns the minimum possible Timedelta."""
        return Timedelta(
            weeks=-sys.maxsize,
            days=0,
            hours=0,
            minutes=0,
            seconds=0,
            milliseconds=0,
            microseconds=0,
            nanoseconds=0,
        )

    @classmethod
    def max(cls) -> 'Timedelta':
        """Returns the maximum possible Timedelta."""
        return Timedelta(
            weeks=sys.maxsize,
            days=6,
            hours=23,
            minutes=59,
            seconds=59,
            milliseconds=999,
            microseconds=999,
            nanoseconds=999,
        )

    @classmethod
    def resolution(cls) -> 'Timedelta':
        """Returns the smallest possible Timedelta resolution (1 nanosecond)."""
        return Timedelta(
            weeks=0,
            days=0,
            hours=0,
            minutes=0,
            seconds=0,
            milliseconds=0,
            microseconds=0,
            nanoseconds=1,
        )

    def __init__(
            self,
            weeks: float | int = 0,
            days: float | int = 0,
            hours: float | int = 0,
            minutes: float | int = 0,
            seconds: float | int = 0,
            milliseconds: float | int = 0,
            microseconds: float | int = 0,
            nanoseconds: float | int = 0,
    ) -> None:
        """
        Initializes a Timedelta instance with the specified time values.

        :param weeks: Number of weeks.
        :param days: Number of days.
        :param hours: Number of hours.
        :param minutes: Number of minutes.
        :param seconds: Number of seconds.
        :param milliseconds: Number of milliseconds.
        :param microseconds: Number of microseconds.
        :param nanoseconds: Number of nanoseconds.
        """
        self._weeks = 0
        self._days = 0
        self._hours = 0
        self._minutes = 0
        self._seconds = 0
        self._milliseconds = 0
        self._microseconds = 0
        self._nanoseconds = 0

        self._add_weeks(weeks=weeks)
        self._add_days(days=days)
        self._add_hours(hours=hours)
        self._add_minutes(minutes=minutes)
        self._add_seconds(seconds=seconds)
        self._add_milliseconds(milliseconds=milliseconds)
        self._add_microseconds(microseconds=microseconds)
        self._add_nanoseconds(nanoseconds=nanoseconds)

    def _add_weeks(self, weeks: float | int) -> None:
        if weeks == 0:
            return

        weeks, days_frac = divmod(weeks, 1)

        self._weeks += int(weeks)
        self._add_days(days=days_frac * 7)

    def _add_days(self, days: float | int) -> None:
        if days == 0:
            return

        days, hours_frac = divmod(days, 1)
        weeks, days = divmod(days + self._days, 7)

        self._days = int(days)
        self._add_weeks(weeks=weeks)
        self._add_hours(hours=hours_frac * 24)

    def _add_hours(self, hours: float | int) -> None:
        if hours == 0:
            return

        hours, minutes_frac = divmod(hours, 1)
        days, hours = divmod(hours + self._hours, 24)

        self._hours = int(hours)
        self._add_days(days=days)
        self._add_minutes(minutes=minutes_frac * 60)

    def _add_minutes(self, minutes: float | int) -> None:
        if minutes == 0:
            return

        minutes, seconds_frac = divmod(minutes, 1)
        hours, minutes = divmod(minutes + self._minutes, 60)

        self._minutes = int(minutes)
        self._add_hours(hours=hours)
        self._add_seconds(seconds=seconds_frac * 60)

    def _add_seconds(self, seconds: float | int) -> None:
        if seconds == 0:
            return

        seconds, milliseconds_frac = divmod(seconds, 1)
        minutes, seconds = divmod(seconds + self._seconds, 60)

        self._seconds = int(seconds)
        self._add_minutes(minutes=minutes)
        self._add_milliseconds(milliseconds=milliseconds_frac * 1000)

    def _add_milliseconds(self, milliseconds: float | int) -> None:
        if milliseconds == 0:
            return

        milliseconds, microseconds_frac = divmod(milliseconds, 1)
        seconds, milliseconds = divmod(milliseconds + self._milliseconds, 1000)

        self._milliseconds = int(milliseconds)
        self._add_seconds(seconds=seconds)
        self._add_microseconds(microseconds=microseconds_frac * 1000)

    def _add_microseconds(self, microseconds: float | int) -> None:
        if microseconds == 0:
            return

        microseconds, nanoseconds_frac = divmod(microseconds, 1)
        milliseconds, microseconds = divmod(microseconds + self._microseconds, 1000)

        self._microseconds = int(microseconds)
        self._add_milliseconds(milliseconds=milliseconds)
        self._add_nanoseconds(nanoseconds=nanoseconds_frac * 1000)

    def _add_nanoseconds(self, nanoseconds: float | int) -> None:
        if nanoseconds == 0:
            return

        nanoseconds = int(nanoseconds)
        microseconds, nanoseconds = divmod(nanoseconds + self._nanoseconds, 1000)

        self._nanoseconds = int(nanoseconds)
        self._add_microseconds(microseconds=microseconds)

    @property
    def is_negative(self) -> bool:
        return self.weeks_portion < 0

    @property
    def weeks_portion(self) -> int:
        return self._weeks

    @property
    def days_portion(self) -> int:
        return self._days

    @property
    def hours_portion(self) -> int:
        return self._hours

    @property
    def minutes_portion(self) -> int:
        return self._minutes

    @property
    def seconds_portion(self) -> int:
        return self._seconds

    @property
    def milliseconds_portion(self) -> int:
        return self._milliseconds

    @property
    def microseconds_portion(self) -> int:
        return self._microseconds

    @property
    def nanoseconds_portion(self) -> int:
        return self._nanoseconds

    def time_portion(self, unit: TimeUnit) -> float:
        return self._portion_time_function_map[unit](self)

    @property
    def total_weeks(self) -> float:
        return self._total_calculation(to_unit=TimeUnit.WEEK)

    @property
    def total_days(self) -> float:
        return self._total_calculation(to_unit=TimeUnit.DAY)

    @property
    def total_hours(self) -> float:
        return self._total_calculation(to_unit=TimeUnit.HOUR)

    @property
    def total_minutes(self) -> float:
        return self._total_calculation(to_unit=TimeUnit.MINUTE)

    @property
    def total_seconds(self) -> float:
        return self._total_calculation(to_unit=TimeUnit.SECOND)

    @property
    def total_milliseconds(self) -> float:
        return self._total_calculation(to_unit=TimeUnit.MILLISECOND)

    @property
    def total_microseconds(self) -> float:
        return self._total_calculation(to_unit=TimeUnit.MICROSECOND)

    @property
    def total_nanoseconds(self) -> float:
        return self._total_calculation(to_unit=TimeUnit.NANOSECOND)

    def _total_calculation(self, to_unit: TimeUnit) -> float:
        table = self._unit_conversion_table
        return (
                self.weeks_portion * table.factor(from_unit=TimeUnit.WEEK, to_unit=to_unit) +
                self.days_portion * table.factor(from_unit=TimeUnit.DAY, to_unit=to_unit) +
                self.hours_portion * table.factor(from_unit=TimeUnit.HOUR, to_unit=to_unit) +
                self.minutes_portion * table.factor(from_unit=TimeUnit.MINUTE, to_unit=to_unit) +
                self.seconds_portion * table.factor(from_unit=TimeUnit.SECOND, to_unit=to_unit) +
                self.milliseconds_portion * table.factor(from_unit=TimeUnit.MILLISECOND, to_unit=to_unit) +
                self.microseconds_portion * table.factor(from_unit=TimeUnit.MICROSECOND, to_unit=to_unit) +
                self.nanoseconds_portion * table.factor(from_unit=TimeUnit.NANOSECOND, to_unit=to_unit)
        )

    def total_time(self, unit: TimeUnit) -> float:
        return self._total_time_function_map[unit](self)

    def __add__(self, other: 'Timedelta') -> 'Timedelta':
        return Timedelta(
            weeks=self.weeks_portion + other.weeks_portion,
            days=self.days_portion + other.days_portion,
            hours=self.hours_portion + other.hours_portion,
            minutes=self.minutes_portion + other.minutes_portion,
            seconds=self.seconds_portion + other.seconds_portion,
            milliseconds=self.milliseconds_portion + other.milliseconds_portion,
            microseconds=self.microseconds_portion + other.microseconds_portion,
            nanoseconds=self.nanoseconds_portion + other.nanoseconds_portion,
        )

    def __sub__(self, other: 'Timedelta') -> 'Timedelta':
        return Timedelta(
            weeks=self.weeks_portion - other.weeks_portion,
            days=self.days_portion - other.days_portion,
            hours=self.hours_portion - other.hours_portion,
            minutes=self.minutes_portion - other.minutes_portion,
            seconds=self.seconds_portion - other.seconds_portion,
            milliseconds=self.milliseconds_portion - other.milliseconds_portion,
            microseconds=self.microseconds_portion - other.microseconds_portion,
            nanoseconds=self.nanoseconds_portion - other.nanoseconds_portion,
        )

    def __neg__(self) -> 'Timedelta':
        return Timedelta(
            weeks=-self.weeks_portion,
            days=-self.days_portion,
            hours=-self.hours_portion,
            minutes=-self.minutes_portion,
            seconds=-self.seconds_portion,
            milliseconds=-self.milliseconds_portion,
            microseconds=-self.microseconds_portion,
            nanoseconds=-self.nanoseconds_portion,
        )

    def __mul__(self, other: int | float) -> 'Timedelta':
        return Timedelta(
            weeks=self.weeks_portion * other,
            days=self.days_portion * other,
            hours=self.hours_portion * other,
            minutes=self.minutes_portion * other,
            seconds=self.seconds_portion * other,
            milliseconds=self.milliseconds_portion * other,
            microseconds=self.microseconds_portion * other,
            nanoseconds=self.nanoseconds_portion * other,
        )

    def __truediv__(self, other: Union[int, float, 'Timedelta']) -> Union[float, 'Timedelta']:
        if isinstance(other, Timedelta):
            return self.total_seconds / other.total_seconds
        else:
            return self * (1 / other)

    def __floordiv__(self, other: Union[int, float, 'Timedelta']) -> Union[int, 'Timedelta']:
        if isinstance(other, Timedelta):
            return int(self.total_seconds // other.total_seconds)
        else:
            return Timedelta(seconds=self.total_seconds // other)

    def __mod__(self, other: 'Timedelta') -> 'Timedelta':
        divider = self // other
        rest = self - other * divider
        return rest

    def __abs__(self) -> 'Timedelta':
        if self.weeks_portion >= 0:
            return deepcopy(self)
        else:
            return -self

    def __divmod__(self, other: 'Timedelta') -> tuple[int, 'Timedelta']:
        quotient, remainder_seconds = divmod(self.total_seconds, other.total_seconds)
        remainder = Timedelta(seconds=remainder_seconds)
        return int(quotient), remainder

    def __iadd__(self, other: 'Timedelta') -> 'Timedelta':
        return self + other

    def __isub__(self, other: 'Timedelta') -> 'Timedelta':
        return self - other

    def __imul__(self, factor: int | float) -> 'Timedelta':
        return self * factor

    def __itruediv__(self, divisor: Union[int, float, 'Timedelta']) -> Union[float, 'Timedelta']:
        return self / divisor

    def __ifloordiv__(self, divisor: Union[int, float, 'Timedelta']) -> Union[int, 'Timedelta']:
        return self // divisor

    def __imod__(self, other: 'Timedelta') -> 'Timedelta':
        return self % other

    def __eq__(self, other: Any) -> bool:
        return (
                isinstance(other, Timedelta) and
                self.weeks_portion == other.weeks_portion and
                self.days_portion == other.days_portion and
                self.hours_portion == other.hours_portion and
                self.minutes_portion == other.minutes_portion and
                self.seconds_portion == other.seconds_portion and
                self.milliseconds_portion == other.seconds_portion and
                self.microseconds_portion == other.microseconds_portion and
                self.nanoseconds_portion == other.nanoseconds_portion
        )

    def __lt__(self, other: 'Timedelta') -> bool:
        return self.total_seconds < other.total_seconds

    def __le__(self, other: 'Timedelta') -> bool:
        return self.total_seconds <= other.total_seconds

    def __gt__(self, other: 'Timedelta') -> bool:
        return self.total_seconds > other.total_seconds

    def __ge__(self, other: 'Timedelta') -> bool:
        return self.total_seconds >= other.total_seconds

    def __str__(self) -> str:
        total = ''

        days = self.weeks_portion * 7 + self.days_portion
        if days != 0:
            total += f'{days} day, ' if days == 1 or days == -1 else f'{days} days, '

        total += f'{self.hours_portion}:{self.minutes_portion:02}:{self.seconds_portion:02}'

        if self.nanoseconds_portion > 0:
            total += (f'.{self.milliseconds_portion:03}{self.microseconds_portion:03}'
                      f'{self.nanoseconds_portion:03}').rstrip('0')
        elif self.microseconds_portion > 0:
            total += f'.{self.milliseconds_portion:03}{self.microseconds_portion:03}'.rstrip('0')
        elif self.milliseconds_portion > 0:
            total += f'.{self.milliseconds_portion:03}'.rstrip('0')

        return total

    def __repr__(self) -> str:
        return (f"Timedelta(weeks={self.weeks_portion}, days={self.days_portion}, hours={self.hours_portion}, "
                f"minutes={self.minutes_portion}, seconds={self.seconds_portion}, "
                f"milliseconds={self.milliseconds_portion}, microseconds={self.microseconds_portion}, "
                f"nanoseconds={self.nanoseconds_portion})")

    def formatted(self, pattern: str, correct_negatives: bool = False) -> str:
        """
        Formats this Timedelta based on the specified pattern.

        :param pattern: A string pattern defining how to format the Timedelta output.
               Available placeholders:
               {w} - weeks, {d} - days, {h} - hours, {m} - minutes, {s} - seconds,
               {ms} - milliseconds, {μs} or {us} - microseconds, {ns} - nanoseconds,
               {sign} - sign.
               Supports format specifiers like {h:02}, {s:.3f}, etc.
               Note that the largest unit placeholder will always be correctly signed.
               Placeholders other than mentioned will be ignored.
        :param correct_negatives: Negative time values are represented by summing a negative base with positive values.
               This means that -0.5s would be depicted as -1.5s (-1s + 500ms = -0.5s).
               If this value is True, this will be adjusted to the correct representation.
        :return: A formatted string representation of this Timedelta.
        """
        matches = [match for match in self._format_spec_regex().finditer(string=pattern)]
        ordered_time_units = TimeUnit.ordered_ascending()
        sorting_key = lambda x: ordered_time_units.index(x)
        used_units = sorted({TimeUnit(match.group('unit')) for match in matches}, key=sorting_key, reverse=True)

        if len(used_units) == 0:
            return pattern

        sign = '-' if self.is_negative else ''
        delta = -self if correct_negatives and self.is_negative else self
        time_for_units = delta._time_value_for_units(used_units=used_units)
        time_for_symbols = {unit.symbol: time_value for unit, time_value in time_for_units.items()}

        def format_match(match: Match) -> str:
            unit = TimeUnit(match.group('unit'))
            spec = match.group('spec')
            spec = ':.0f' if spec is None else spec
            spec = f'{spec}.0f' if not '.' in spec else spec
            formatted = f'{{{spec}}}'.format(time_for_symbols[unit.symbol])
            return f'{sign}{formatted}' if correct_negatives and unit == used_units[0] else formatted

        pattern = pattern.replace('{sign}', sign)
        for match in matches:
            pattern = pattern.replace(match.group('all'), format_match(match=match))

        return pattern

    def _time_value_for_units(self, used_units: list[TimeUnit]) -> dict[TimeUnit, float]:
        time_for_unit = {}
        processed_units = set()
        for unit in used_units:
            time_value = 0.0
            greater_units = set(unit.greater_units_ascending)

            for greater_unit in greater_units - processed_units:
                time_portion = self.time_portion(unit=greater_unit)
                time_value += self._unit_conversion_table.factor(from_unit=greater_unit, to_unit=unit) * time_portion

            time_value += self.time_portion(unit=unit)

            processed_units.update(greater_units)
            processed_units.add(unit)
            time_for_unit[unit] = time_value

        smallest_used_unit = used_units[-1]
        time_for_unit[smallest_used_unit] += sum([
            self._unit_conversion_table.factor(from_unit=unit, to_unit=smallest_used_unit)
            for unit in smallest_used_unit.smaller_units_descending
        ])
        return time_for_unit
