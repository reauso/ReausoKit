import re
import time
from collections import defaultdict
from collections.abc import Hashable
from dataclasses import dataclass
from multiprocessing import RLock, Lock
from typing import TypeVar, TypeVarTuple, Self

from sortedcontainers import SortedList

from rkit.patterns import Singleton
from rkit.string import replace_multiple
from rkit.time import Timedelta

Ts = TypeVarTuple('Ts')
R = TypeVar('R')


class Stopwatch:
    def __init__(self) -> None:
        """Initializes the Stopwatch with empty start, pause, and lap time records."""
        self._start_times: dict[Hashable | None, int] = {}
        self._pause_times: dict[Hashable | None, int] = {}
        self._lap_times: dict[Hashable | None, list[Timedelta]] = defaultdict(list)

    def start(self, tag: Hashable | None = None) -> None:
        """Starts or restarts the stopwatch for a given tag."""
        self.reset_tag(tag=tag)
        self._start_times[tag] = time.perf_counter_ns()

    def pause(self, tag: Hashable | None = None) -> None:
        """Pauses the stopwatch for a given tag."""
        if not self.is_started(tag=tag):
            raise RuntimeError(f"Stopwatch for tag '{tag}' is not started.")

        if self.is_running(tag=tag):
            self._pause_times[tag] = time.perf_counter_ns()

    def unpause(self, tag: Hashable | None = None) -> None:
        """Resumes the stopwatch from a paused state for a given tag."""
        if self.is_paused(tag=tag):
            self._start_times[tag] += time.perf_counter_ns() - self._pause_times[tag]
            del self._pause_times[tag]

    def lap(self, tag: Hashable | None = None) -> Timedelta:
        """Records a lap time for a given tag and returns the elapsed time."""
        elapsed = self.elapsed(tag=tag)
        self._lap_times[tag].append(elapsed)
        return elapsed

    def stop(self, tag: Hashable | None = None) -> Timedelta:
        """Records a lap time, stops the stopwatch for a given tag and returns the last elapsed time."""
        elapsed = self.lap(tag=tag)
        del self._start_times[tag]
        return elapsed

    def reset(self) -> None:
        """Resets all stored times, clearing all stopwatch records."""
        self._start_times.clear()
        self._pause_times.clear()
        self._lap_times.clear()

    def reset_tag(self, tag: Hashable | None = None) -> None:
        """Resets the stopwatch data for a specific tag."""
        self._start_times.pop(tag, None)
        self._pause_times.pop(tag, None)
        self._lap_times.pop(tag, None)

    def elapsed(self, tag: Hashable | None = None) -> Timedelta:
        """Returns the elapsed time for a given tag without adding a new lap."""
        if not self.is_running(tag=tag):
            raise RuntimeError(f"Stopwatch for tag '{tag}' is not running.")

        elapsed_ns = time.perf_counter_ns() - self._start_times[tag]
        return Timedelta(nanoseconds=elapsed_ns)

    def lap_time(self, tag: Hashable | None = None, lap: int = -1) -> Timedelta:
        """Returns the time of a specific lap for a given tag."""
        if tag not in self._lap_times:
            return Timedelta(nanoseconds=0)
        if lap == 0:
            raise ValueError("Expected lap id other than zero.")

        lap = lap + 1 if lap < 0 else lap
        return self._lap_times[tag][lap - 1]

    def elapsed_since(self, since_lap: int, tag: Hashable | None = None) -> Timedelta:
        """Returns the time difference between the elapsed time and a lap for a given tag."""
        elapsed_time = self.elapsed(tag=tag)
        return self._delta_since_lap(delta=elapsed_time, since_lap=since_lap, tag=tag)

    def lap_time_since(self, since_lap: int, tag: Hashable | None = None, lap: int = -1) -> Timedelta:
        """Returns the time difference between two laps for a given tag."""
        total = self.lap_time(lap=lap, tag=tag)
        return self._delta_since_lap(delta=total, since_lap=since_lap, tag=tag)

    def _delta_since_lap(self, delta: Timedelta, since_lap: int, tag: Hashable | None) -> Timedelta:
        """Returns the time difference between a timedelta and a lap time for a given tag."""
        since_lap = 0 if since_lap + self.num_laps(tag=tag) == -1 else since_lap
        since_lap_time = Timedelta() if since_lap == 0 else self.lap_time(lap=since_lap, tag=tag)
        return delta - since_lap_time

    def elapsed_since_previous_lap(self, tag: Hashable | None = None) -> Timedelta:
        """Returns the time difference between the elapsed time and the latest lap time."""
        return self.elapsed_since(since_lap=-1, tag=tag)

    def lap_time_since_previous_lap(self, tag: Hashable | None = None, lap: int = -1) -> Timedelta:
        """Returns the time difference between the current lap and the previous one."""
        return self.lap_time_since(lap=lap, since_lap=lap - 1, tag=tag)

    def get_laps(self, tag: Hashable | None = None) -> tuple[Timedelta, ...]:
        """Returns all lap times recorded for a given tag as a tuple."""
        return tuple(self._lap_times.get(tag, list()))

    def num_laps(self, tag: Hashable | None = None) -> int:
        """Returns the number of laps recorded for a given tag."""
        return len(self._lap_times.get(tag, tuple()))

    def __contains__(self, tag: Hashable | None) -> bool:
        """Checks if a given tag exists in the stopwatch records."""
        return tag in self._start_times or tag in self._lap_times

    def is_started(self, tag: Hashable | None = None) -> bool:
        """Returns whether the stopwatch has been started for a given tag."""
        return tag in self._start_times

    def is_paused(self, tag: Hashable | None = None) -> bool:
        """Returns whether the stopwatch is paused for a given tag."""
        return tag in self._pause_times

    def is_running(self, tag: Hashable | None = None) -> bool:
        """Returns whether the stopwatch is currently running for a given tag."""
        return self.is_started(tag=tag) and not self.is_paused(tag=tag)

    def is_stopped(self, tag: Hashable | None = None) -> bool:
        """Returns whether the stopwatch is stopped for a given tag."""
        return not self.is_started(tag=tag) and tag in self._lap_times


class TimeMeasure(Stopwatch):
    _since_lap_regex = re.compile(r"(?P<all>{since_(?P<since_lap>-?\d+)})")

    def __init__(
            self,
            timedelta_pattern: str = "{h}:{m:02}:{s:02}.{ms:03}{μs:03}{ns:03}",
            timedelta_negative_correction: bool = True,
    ) -> None:
        """
        Initializes the TimeMeasure instance with a specific format pattern.

        :param timedelta_pattern: A string pattern defining how to format the Timedelta output.
               Available placeholders:
               {w} - weeks, {d} - days, {h} - hours, {m} - minutes, {s} - seconds,
               {ms} - milliseconds, {μs} or {us} - microseconds, {ns} - nanoseconds,
               {sign} - sign.
               Supports format specifiers like {h:02}, {s:.3f}, etc.
               Note that the largest unit placeholder will always be correctly signed.
               Placeholders other than mentioned will be ignored.
        :param timedelta_negative_correction: Negative time values are represented by summing a negative base
               with positive values. This means that -0.5s would be depicted as -1.5s (-1s + 500ms = -0.5s).
               If this value is True, this will be adjusted to the correct representation.
        """
        super().__init__()
        self._timedelta_pattern = timedelta_pattern
        self._correct_negatives = timedelta_negative_correction

    @property
    def timedelta_pattern(self) -> str:
        return self._timedelta_pattern

    @timedelta_pattern.setter
    def timedelta_pattern(self, pattern: str) -> None:
        self._timedelta_pattern = pattern

    @property
    def timedelta_negative_correction(self) -> bool:
        return self._correct_negatives

    @timedelta_negative_correction.setter
    def timedelta_negative_correction(self, timedelta_negative_correction: bool) -> None:
        self._correct_negatives = timedelta_negative_correction

    def formatted_elapsed_time(self, tag: Hashable | None = None) -> str:
        elapsed = self.elapsed(tag=tag)
        return elapsed.formatted(pattern=self._timedelta_pattern, correct_negatives=self._correct_negatives)

    def formatted_lap_time(self, tag: Hashable | None = None, lap: int = -1) -> str:
        lap_time = self.lap_time(lap=lap, tag=tag)
        return lap_time.formatted(pattern=self._timedelta_pattern, correct_negatives=self._correct_negatives)

    def formatted_lap_time_since(self, since_lap: int, tag: Hashable | None = None, lap: int = -1) -> str:
        lap_time_since = self.lap_time_since(lap=lap, since_lap=since_lap, tag=tag)
        return lap_time_since.formatted(pattern=self._timedelta_pattern, correct_negatives=self._correct_negatives)

    def formatted_lap_time_since_previous_lap(self, tag: Hashable | None = None, lap: int = -1) -> str:
        lap_time_since = self.lap_time_since_previous_lap(lap=lap, tag=tag)
        return lap_time_since.formatted(pattern=self._timedelta_pattern, correct_negatives=self._correct_negatives)

    def all_formatted_lap_times(self, tag: Hashable | None = None) -> tuple[str, ...]:
        return tuple(
            delta.formatted(pattern=self._timedelta_pattern, correct_negatives=self._correct_negatives)
            for delta in self.get_laps(tag=tag)
        )

    def formatted_elapsed_message(
            self,
            tag: Hashable | None = None,
            pattern: str = "Elapsed {timedelta} for tag '{tag}'."
    ) -> str:
        elapsed = self.elapsed(tag=tag)
        formatted = elapsed.formatted(pattern=self._timedelta_pattern, correct_negatives=self._correct_negatives)
        replacements = {
            '{tag}': str(tag),
            '{timedelta}': formatted,
            '{since_previous}': '{since_-1}',
        }
        pattern = replace_multiple(s=pattern, replacements=replacements)
        replacements = self._formatted_since_replacements(elapsed=elapsed, tag=tag, pattern=pattern)
        pattern = replace_multiple(s=pattern, replacements=replacements)

        return pattern

    def formatted_lap_message(
            self,
            tag: Hashable | None = None,
            lap: int = -1,
            pattern: str = "Lap {lap} Time {timedelta} of tag '{tag}'. {since_previous} since previous."
    ) -> str:
        lap_time = self.lap_time(lap=lap, tag=tag)
        formatted = lap_time.formatted(pattern=self._timedelta_pattern, correct_negatives=self._correct_negatives)
        replacements = {
            '{tag}': str(tag),
            '{lap}': str(lap) if lap >= 0 else str(self.num_laps(tag=tag) + lap + 1),
            '{timedelta}': formatted,
            '{since_previous}': f'{"{since_"}{str(lap - 1)}{"}"}',
        }
        pattern = replace_multiple(s=pattern, replacements=replacements)
        replacements = self._formatted_since_replacements(elapsed=lap_time, tag=tag, pattern=pattern)
        pattern = replace_multiple(s=pattern, replacements=replacements)

        return pattern

    def all_formatted_lap_messages(
            self,
            tag: Hashable | None = None,
            pattern: str = "Lap {lap} Time {timedelta} of tag '{tag}'. {since_previous} since previous."
    ) -> tuple[str, ...]:
        return tuple(
            self.formatted_lap_message(lap=i + 1, tag=tag, pattern=pattern) for i in range(self.num_laps(tag=tag))
        )

    def _formatted_since_replacements(self, elapsed: Timedelta, tag: Hashable | None, pattern: str) -> dict[str, str]:
        matches = self._since_lap_regex.finditer(string=pattern)
        replacements = {
            match.group('all'): self._formatted_delta_since_lap(
                delta=elapsed,
                since_lap=int(match.group('since_lap')),
                tag=tag,
            )
            for match in matches
        }
        return replacements

    def _formatted_delta_since_lap(self, delta: Timedelta, since_lap: int, tag: Hashable | None) -> str:
        delta = self._delta_since_lap(delta=delta, since_lap=since_lap, tag=tag)
        return delta.formatted(pattern=self._timedelta_pattern, correct_negatives=self._correct_negatives)

    def stop_and_format_message(
            self,
            tag: Hashable | None = None,
            pattern: str = "Stopped after {timedelta} for tag '{tag}'."
    ) -> str:
        self.stop(tag=tag)
        return self.formatted_lap_message(lap=-1, tag=tag, pattern=pattern)

    def lap_and_format_message(
            self,
            tag: Hashable | None = None,
            pattern: str = "Lap {lap} Time {timedelta} of tag '{tag}'. {since_previous} since previous."
    ) -> str:
        self.lap(tag=tag)
        return self.formatted_lap_message(lap=-1, tag=tag, pattern=pattern)


@Singleton
class GlobalTimeMeasureRegister:
    def __init__(self) -> None:
        self._lock = Lock()
        self._time_measures: dict[Hashable | None, TimeMeasure] = {}

    def new(
            self,
            idx: Hashable | None = None,
            timedelta_pattern: str = "{h}:{m:02}:{s:02}.{ms:03}{μs:03}{ns:03}",
    ) -> TimeMeasure:
        with self._lock:
            self._time_measures[idx] = TimeMeasure(timedelta_pattern=timedelta_pattern)
            return self._time_measures[idx]

    def add(self, time_measure: TimeMeasure, idx: Hashable | None = None) -> None:
        with self._lock:
            self._time_measures[idx] = time_measure

    def remove(self, idx: Hashable | None = None) -> None:
        with self._lock:
            self._time_measures.pop(idx, None)

    def clear(self) -> None:
        with self._lock:
            self._time_measures.clear()

    def time_measure(self, idx: Hashable | None = None) -> TimeMeasure:
        with self._lock:
            return self._time_measures[idx]

    def __contains__(self, idx: Hashable) -> bool:
        with self._lock:
            return idx in self._time_measures


@dataclass(kw_only=True, frozen=True)
class TimelineEvent:
    elapsed: Timedelta
    tag: Hashable | None
    description: str | None

    def __lt__(self, other: Self) -> bool:
        return self.elapsed < other.elapsed

    def formatted(
            self,
            pattern: str = '{h}:{m:02}:{s:02}.{ms:03}{us:03} - {tag}: {description}',
            timedelta_negative_correction: bool = True,
    ) -> str:
        pattern = self.elapsed.formatted(pattern=pattern, correct_negatives=timedelta_negative_correction)
        replacements = {
            '{tag}': str(self.tag),
            '{description}': str(self.description),
        }
        pattern = replace_multiple(s=pattern, replacements=replacements)
        return pattern

    def __str__(self) -> str:
        return self.formatted()


class Timeline:
    _since_event_regex = re.compile(r"(?P<all>{since_(?P<since_index>-?\d+)})")
    _since_tag_event_regex = re.compile(r"(?P<all>{since_tag_(?P<since_index>-?\d+)})")

    def __init__(
            self,
            timedelta_pattern: str = '{m}:{s:02}.{ms:03}{us:03}',
            timedelta_negative_correction: bool = True,
    ) -> None:
        self._lock = RLock()
        self._timedelta_pattern = timedelta_pattern
        self._events: SortedList[TimelineEvent] = SortedList()
        self._tag_events: dict[Hashable | None, SortedList[TimelineEvent]] = defaultdict(SortedList)
        self._start_time = time.perf_counter_ns()
        self._correct_negatives = timedelta_negative_correction

    @property
    def timedelta_pattern(self) -> str:
        return self._timedelta_pattern

    @timedelta_pattern.setter
    def timedelta_pattern(self, pattern: str) -> None:
        self._timedelta_pattern = pattern

    @property
    def timedelta_negative_correction(self) -> bool:
        return self._correct_negatives

    @timedelta_negative_correction.setter
    def timedelta_negative_correction(self, timedelta_negative_correction: bool) -> None:
        self._correct_negatives = timedelta_negative_correction

    @property
    def tags(self) -> set[Hashable | None]:
        return set(self._tag_events.keys())

    @property
    def elapsed(self) -> Timedelta:
        elapsed_ns = time.perf_counter_ns() - self._start_time
        return Timedelta(nanoseconds=elapsed_ns)

    def add(self, tag: Hashable | None = None, description: str | None = None) -> TimelineEvent:
        elapsed = self.elapsed
        event = TimelineEvent(
            elapsed=elapsed,
            tag=tag,
            description=description,
        )
        with self._lock:
            self._events.add(event)
            self._tag_events[tag].add(event)

        return event

    def fadd(
            self,
            tag: Hashable | None = None,
            description: str | None = None,
            post: str = '',
            pattern: str = '{elapsed} elapsed | {since_tag_previous} since previous tag - {tag}: {description} {post}',
    ) -> str:
        event = self.add(tag=tag, description=description)
        return self._formatted_event(event=event, post=post, pattern=pattern)

    @property
    def events(self) -> tuple[TimelineEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def tag_events(self, tag: Hashable | None = None) -> tuple[TimelineEvent, ...]:
        with self._lock:
            return tuple(self._tag_events.get(tag, []))

    def formatted_events(
            self,
            post: str = '',
            pattern: str = '{elapsed} elapsed | {since_tag_previous} since previous tag - {tag}: {description} {post}',
    ) -> tuple[str, ...]:
        return tuple(
            self._formatted_event(event=event, post=post, pattern=pattern) for event in self.events
        )

    def formatted_tag_events(
            self,
            tag: Hashable | None = None,
            post: str = '',
            pattern: str = '{elapsed} elapsed | {since_tag_previous} since previous tag - {tag}: {description} {post}',
    ) -> tuple[str, ...]:
        return tuple(
            self._formatted_event(event=event, post=post, pattern=pattern) for event in self.tag_events(tag=tag)
        )

    def _formatted_event(self, event: TimelineEvent, post: str, pattern: str) -> str:
        pattern = self._parse_pattern(pattern=pattern, event=event, post=post)
        replacements = self._formatted_since_replacements(event=event, pattern=pattern)
        pattern = replace_multiple(s=pattern, replacements=replacements)
        return event.formatted(pattern=pattern, timedelta_negative_correction=self._correct_negatives)

    def _parse_pattern(self, pattern: str, event: TimelineEvent, post: str) -> str:
        event_index = self._events.index(value=event)
        tag_event_index = self._tag_events[event.tag].index(value=event)

        since_previous = f'{"{since_"}{event_index - 1}{"}"}'
        since_tag_previous = f'{"{since_tag_"}{tag_event_index - 1}{"}"}'

        replacements = {
            '{elapsed}': self._timedelta_pattern,
            '{timedelta}': self._timedelta_pattern,
            '{post}': post,
            '{index}': str(event_index),
            '{tag_index}': str(tag_event_index),
            '{since_previous}': since_previous if event_index > 0 else self._timedelta_pattern,
            '{since_tag_previous}': since_tag_previous if tag_event_index > 0 else self._timedelta_pattern,
        }
        return replace_multiple(s=pattern, replacements=replacements)

    def _formatted_since_replacements(self, event: TimelineEvent, pattern: str) -> dict[str, str]:
        matches = self._since_event_regex.finditer(string=pattern)
        replacements = {
            match.group('all'): self._formatted_delta_since(
                event=event, event_list=self._events, index=int(match.group('since_index'))
            ) for match in matches
        }
        matches = self._since_tag_event_regex.finditer(string=pattern)
        replacements.update({
            match.group('all'): self._formatted_delta_since(
                event=event, event_list=self._tag_events[event.tag], index=int(match.group('since_index'))
            ) for match in matches
        })
        return replacements

    def _formatted_delta_since(self, event: TimelineEvent, event_list: SortedList[TimelineEvent], index: int) -> str:
        delta = self._delta_since(event=event, event_list=event_list, index=index)
        return delta.formatted(pattern=self._timedelta_pattern, correct_negatives=self._correct_negatives)

    @classmethod
    def _delta_since(cls, event: TimelineEvent, event_list: SortedList[TimelineEvent], index: int) -> Timedelta:
        if len(event_list) + index == -1:
            return event.elapsed

        return event.elapsed - event_list[index].elapsed

    def __len__(self) -> int:
        with self._lock:
            return len(self._events)

    def contains_tag(self, tag: Hashable | None = None) -> bool:
        with self._lock:
            return tag in self._tag_events

    def __str__(self) -> str:
        pattern = '{elapsed} elapsed | {since_tag_previous} since previous tag - {tag}: {description}'
        events = "\n\t".join(self.formatted_events(pattern=pattern))
        events = f'\t{events}\n' if events != '' else events
        return (
            'Timeline'
            '[\n'
            f'{events}'
            ']'
        )


@Singleton
class GlobalTimelineRegister:
    def __init__(self) -> None:
        self._lock = Lock()
        self._timelines: dict[Hashable | None, Timeline] = {}

    def new(
            self,
            idx: Hashable | None = None,
            timedelta_pattern: str = '{m}:{s:02}.{ms:03}{us:03}',
    ) -> Timeline:
        with self._lock:
            self._timelines[idx] = Timeline(timedelta_pattern=timedelta_pattern)
            return self._timelines[idx]

    def add(self, timeline: Timeline, idx: Hashable | None = None) -> None:
        with self._lock:
            self._timelines[idx] = timeline

    def remove(self, idx: Hashable | None = None) -> None:
        with self._lock:
            self._timelines.pop(idx, None)

    def clear(self) -> None:
        with self._lock:
            self._timelines.clear()

    def timeline(self, idx: Hashable | None = None) -> Timeline:
        with self._lock:
            return self._timelines[idx]

    def __contains__(self, idx: Hashable) -> bool:
        with self._lock:
            return idx in self._timelines
