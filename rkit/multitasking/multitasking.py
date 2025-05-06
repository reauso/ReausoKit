from traceback import format_exception

import threading

from collections.abc import Callable

from typing import Union, Self, Any, Iterable, TypeVarTuple, Generic, TypeVar

from bisect import insort
from enum import StrEnum, auto
from threading import Thread, Lock, RLock, Condition, Event

from rkit.design_patterns import ParameterizedObserver

_TPs = TypeVarTuple('_TPs')
_TR = TypeVar('_TR')
_Task = TypeVar('_T', bound='_TaskBase')
Immutable = Union[int | float | str | tuple]


# TODO doc
# TODO test


class TaskException(Exception, Generic[_Task]):
    def __init__(self, message, task: _Task) -> None:
        super().__init__(message)
        self._task = task

    @property
    def task(self) -> _Task:
        return self._task


class TaskExecutionException(TaskException):
    def __init__(self, message, task: _Task) -> None:
        super().__init__(message, task=task)


class TaskPrerequisiteException(TaskException):
    def __init__(self, message, task: _Task) -> None:
        super().__init__(message, task=task)


class TaskState(StrEnum):
    Creating = auto()
    Prerequisites_Unfulfilled = auto()
    Executable = auto()
    Running = auto()
    Successful = auto()
    Failed = auto()
    Prerequisite_Failed = auto()

    @classmethod
    def submitted_states(cls) -> list['TaskState']:
        return [cls.Executable, cls.Prerequisites_Unfulfilled]

    @classmethod
    def determined_states(cls) -> list['TaskState']:
        return [cls.Successful, cls.Failed, cls.Prerequisite_Failed]

    @classmethod
    def failed_states(cls) -> list['TaskState']:
        return [cls.Failed, cls.Prerequisite_Failed]


class TaskGroupCollection:
    # TODO rework,
    #  - dynamic group prerequisites (needs group monitoring)
    #  - TaskGroup class to simplify this implementation
    def __init__(self) -> None:
        self._groups: dict[Immutable, list[Task]] = {}

    def set_group_with_prerequisite(
            self,
            identifier: Immutable,
            tasks: list['Task'],
            prerequisite_groups: Iterable[Immutable],
    ) -> None:
        prerequisite_groups = set(prerequisite_groups)

        for group in prerequisite_groups:
            if group not in self._groups:
                raise ValueError(f"No existing group with identifier '{group}'.")

        self[identifier] = list(tasks)

        if len(prerequisite_groups) == 0:
            return
        self._add_prerequisites_to_tasks(prerequisite_groups, tasks)

    def _add_prerequisites_to_tasks(self, prerequisite_groups: set[Immutable], tasks: list['Task']):
        prerequisite_tasks = [task for identifier in prerequisite_groups for task in self[identifier]]
        for task in tasks:
            if task.prerequisites:
                task.prerequisites.add_tasks(new_tasks=prerequisite_tasks)
            else:
                task.prerequisites = prerequisite_tasks

    def __setitem__(self, identifier: Immutable, tasks: list['Task']) -> None:
        if not isinstance(identifier, Immutable):
            raise TypeError(f"group identifier must be immutable.")
        if not isinstance(tasks, list) or any([not isinstance(task, Task) for task in tasks]):
            raise TypeError(f"value must be of type list[_Task]")

        self._groups[identifier] = list(tasks)

    def __getitem__(self, identifier: Immutable) -> list['Task']:
        if not isinstance(identifier, Immutable):
            raise TypeError(f"group identifier must be immutable.")
        if identifier not in self._groups:
            raise ValueError(f"No existing group with identifier '{identifier}'.")

        return self._groups[identifier]

    def __delitem__(self, identifier: Immutable) -> None:
        if not isinstance(identifier, Immutable):
            raise TypeError(f"group identifier must be immutable.")
        if identifier not in self._groups:
            raise ValueError(f"No existing group with identifier '{identifier}'.")

        del self._groups[identifier]

    @property
    def group_identifiers(self) -> list[Immutable]:
        return list(self._groups.keys())

    def group_size(self, identifier: Immutable) -> int:
        return len(self[identifier])

    def is_printing_state_changes_for_group(self, identifier: Immutable) -> bool:
        return all([task.is_printing_state_changes for task in self[identifier]])

    def set_print_state_change_for_group(self, identifier: Immutable, value: bool) -> None:
        for task in self[identifier]:
            task.is_printing_state_changes = value

    @property
    def is_printing_state_changes(self) -> bool:
        return all([task.is_printing_state_changes for task in self.all_tasks])

    @is_printing_state_changes.setter
    def is_printing_state_changes(self, value: bool) -> None:
        for task in self.all_tasks:
            task.is_printing_state_changes = value

    @property
    def all_tasks(self) -> list['Task']:
        return [task for group in self._groups.values() for task in group]

    def __len__(self) -> int:
        return sum([len(group) for group in self._groups.values()])

    @property
    def unsubmitted_tasks(self) -> list['Task']:
        return [task for task in self.all_tasks if task.state is TaskState.Creating]

    @property
    def num_unsubmitted_tasks(self) -> int:
        return len(self.unsubmitted_tasks)


class TaskMonitoring:
    @staticmethod
    def from_groups(groups: TaskGroupCollection) -> 'TaskMonitoring':
        return TaskMonitoring(tasks=groups.all_tasks)

    def __init__(self, tasks: list['Task'] = None) -> None:
        self._mutex = RLock()
        self._tasks_per_state: dict[TaskState, list[Task]] = {TaskState(state): [] for state in list(TaskState)}
        self._change_observer = ParameterizedObserver['TaskSupervisor']()

        if tasks:
            self.add_tasks(new_tasks=tasks)

    def __iadd__(self, new_tasks: Union['Task', list['Task']]) -> Self:
        new_tasks = [new_tasks] if isinstance(new_tasks, Task) else new_tasks
        self.add_tasks(new_tasks=new_tasks)
        return self

    def __isub__(self, remove_tasks: Union['Task', list['Task']]) -> Self:
        remove_tasks = [remove_tasks] if isinstance(remove_tasks, Task) else remove_tasks
        self.remove_tasks(remove_tasks=remove_tasks)
        return self

    def add_tasks(self, new_tasks: list['Task']) -> None:
        self._validate_is_task_list(task_list=new_tasks)

        with self._mutex:
            for task in new_tasks:
                self._tasks_per_state[task.state].append(task)
                task.add_state_change_listener(self._task_state_changed_listener)

        self._change_observer.notify_listeners(self)

    def remove_tasks(self, remove_tasks: list['Task']) -> None:
        self._validate_is_task_list(task_list=remove_tasks)

        with self._mutex:
            for task in remove_tasks:
                task.remove_state_change_listener(self._task_state_changed_listener)
                self._tasks_per_state[task.state].remove(task)

        self._change_observer.notify_listeners(self)

    def clear_tasks(self) -> None:
        all_tasks = [task for task_list in self._tasks_per_state.values() for task in task_list]
        self.remove_tasks(remove_tasks=all_tasks)

    @classmethod
    def _validate_is_task_list(cls, task_list: Any):
        if not isinstance(task_list, list):
            raise TypeError('Parameter has to be a list.')

        for entry in task_list:
            if not isinstance(entry, Task):
                raise TypeError('List entries have to be Tasks.')

    def _task_state_changed_listener(self, task: 'Task', previous_state: TaskState):
        with self._mutex:
            if task in self._tasks_per_state[previous_state]:
                self._tasks_per_state[previous_state].remove(task)
            self._tasks_per_state[task.state].append(task)

        self._change_observer.notify_listeners(self)

    def add_change_listener(self, listener: Callable[['TaskMonitoring'], None]) -> None:
        self._change_observer.add_listener(listener=listener)

    def remove_change_listener(self, listener: Callable[['TaskMonitoring'], None]) -> None:
        self._change_observer.remove_listener(listener=listener)

    @property
    def statistics(self) -> dict[str, int]:
        with self._mutex:
            return {key: len(value) for key, value in self._tasks_per_state.items()}

    def __len__(self) -> int:
        return sum([len(task_list) for task_list in self._tasks_per_state.values()])

    def __contains__(self, item: Any) -> bool:
        if not isinstance(item, Task):
            raise TypeError('item has to be a Task.')

        is_in_task_list = [item in task_list for task_list in self._tasks_per_state.values()]
        return any(is_in_task_list)

    @property
    def num_created_tasks(self) -> int:
        with self._mutex:
            return len(self._tasks_per_state[TaskState.Creating])

    @property
    def num_executable_tasks(self) -> int:
        with self._mutex:
            return len(self._tasks_per_state[TaskState.Executable])

    @property
    def num_prerequisites_unfulfilled(self) -> int:
        with self._mutex:
            return len(self._tasks_per_state[TaskState.Prerequisites_Unfulfilled])

    @property
    def num_submitted_tasks(self) -> int:
        with self._mutex:
            num_sum = 0
            for state in TaskState.submitted_states():
                num_sum += len(self._tasks_per_state[state])
            return num_sum

    @property
    def num_running_tasks(self) -> int:
        with self._mutex:
            return len(self._tasks_per_state[TaskState.Running])

    @property
    def num_successful_tasks(self) -> int:
        with self._mutex:
            return len(self._tasks_per_state[TaskState.Successful])

    @property
    def num_failed_tasks(self) -> int:
        with self._mutex:
            return len(self._tasks_per_state[TaskState.Failed])

    @property
    def num_prerequisites_failed_tasks(self) -> int:
        with self._mutex:
            return len(self._tasks_per_state[TaskState.Prerequisite_Failed])

    @property
    def num_tasks_with_determined_results(self) -> int:
        with self._mutex:
            num_sum = 0
            for state in TaskState.determined_states():
                num_sum += len(self._tasks_per_state[state])
            return num_sum

    @property
    def num_tasks_with_undetermined_results(self) -> int:
        with self._mutex:
            return len(self) - self.num_tasks_with_determined_results

    @property
    def all_tasks_have_been_submitted(self) -> bool:
        with self._mutex:
            return self.num_created_tasks == 0

    @property
    def all_task_results_have_been_determined(self) -> bool:
        with self._mutex:
            return self.num_tasks_with_undetermined_results == 0


class TaskBarrier(TaskMonitoring):
    @staticmethod
    def from_groups(groups: TaskGroupCollection) -> 'TaskBarrier':
        return TaskBarrier(tasks=groups.all_tasks)

    def __init__(self, tasks: list['Task'] = None) -> None:
        super().__init__(tasks=tasks)
        self._change_condition = Condition(self._mutex)
        self.add_change_listener(self._change_listener)

    def _change_listener(self, _):
        with self._change_condition:
            self._change_condition.notify_all()

    def wait_until_all_tasks_have_been_submitted(self, timeout_seconds: float = None) -> bool:
        with self._change_condition:
            return self._change_condition.wait_for(
                predicate=lambda: self.all_tasks_have_been_submitted,
                timeout=timeout_seconds,
            )

    def wait_until_all_task_results_have_been_determined(self, timeout_seconds: float = None) -> bool:
        with self._change_condition:
            return self._change_condition.wait_for(
                predicate=lambda: self.all_task_results_have_been_determined,
                timeout=timeout_seconds,
            )


class TaskPrerequisitesState(StrEnum):
    Unfulfilled = auto()
    Fulfilled = auto()
    Unfulfillable = auto()


class TaskPrerequisites(TaskMonitoring):
    @staticmethod
    def from_groups(groups: TaskGroupCollection) -> 'TaskPrerequisites':
        return TaskPrerequisites(tasks=groups.all_tasks)

    def __init__(self, tasks: list['Task'] = None) -> None:
        self._is_locked = False
        super().__init__(tasks=tasks)
        self._state_observer = ParameterizedObserver['TaskPrerequisites', TaskPrerequisitesState]()
        self._state: TaskPrerequisitesState = self._current_state()

        self.add_change_listener(self._change_listener)

    def _change_listener(self, _):
        with self._mutex:
            self.state = self._current_state()

    def _current_state(self) -> TaskPrerequisitesState:
        with self._mutex:
            if self.num_failed_tasks > 0:
                return TaskPrerequisitesState.Unfulfillable
            elif self.num_unfulfilled_prerequisites > 0:
                return TaskPrerequisitesState.Unfulfilled
            else:
                return TaskPrerequisitesState.Fulfilled

    def add_tasks(self, new_tasks: list['Task']) -> None:
        if self.is_locked:
            raise RuntimeError(f'Cannot add Tasks to locked {self.__class__.__name__}.')

        super().add_tasks(new_tasks=new_tasks)

    def remove_tasks(self, remove_tasks: list['Task']) -> None:
        if self.is_locked:
            raise RuntimeError(f'Cannot remove Tasks from locked {self.__class__.__name__}.')

        super().remove_tasks(remove_tasks=remove_tasks)

    def cleat_tasks(self) -> None:
        if self.is_locked:
            raise RuntimeError(f'Cannot remove Tasks from locked {self.__class__.__name__}.')

        super().clear_tasks()

    @property
    def num_unfulfilled_prerequisites(self) -> int:
        with self._mutex:
            return self.num_created_tasks + self.num_submitted_tasks + self.num_running_tasks

    @property
    def num_fulfilled_prerequisites(self) -> int:
        with self._mutex:
            return self.num_successful_tasks

    @property
    def num_unfulfillable_prerequisites(self) -> int:
        with self._mutex:
            return self.num_failed_tasks + self.num_prerequisites_failed_tasks

    @property
    def state(self) -> TaskPrerequisitesState:
        with self._mutex:
            return self._state

    @state.setter
    def state(self, new_state: TaskPrerequisitesState) -> None:
        with self._mutex:
            previous_state = self._state
            self._state = new_state

            if new_state != previous_state:
                self._state_observer.notify_listeners(self, previous_state)

    @property
    def unfulfilled_tasks(self) -> list['Task']:
        tasks = []
        tasks.extend(self._tasks_per_state[TaskState.Creating])
        tasks.extend(self._tasks_per_state[TaskState.Executable])
        tasks.extend(self._tasks_per_state[TaskState.Prerequisites_Unfulfilled])
        tasks.extend(self._tasks_per_state[TaskState.Running])
        return tasks

    @property
    def fulfilled_tasks(self) -> list['Task']:
        tasks = []
        tasks.extend(self._tasks_per_state[TaskState.Successful])
        return tasks

    @property
    def failed_tasks(self) -> list['Task']:
        tasks = []
        tasks.extend(self._tasks_per_state[TaskState.Failed])
        tasks.extend(self._tasks_per_state[TaskState.Prerequisite_Failed])
        return tasks

    @property
    def is_locked(self) -> bool:
        return self._is_locked

    def lock(self) -> None:
        with self._mutex:
            self._is_locked = True

    def add_state_change_listener(
            self, listener: Callable[['TaskPrerequisites', TaskPrerequisitesState], None]) -> None:
        self._state_observer.add_listener(listener=listener)

    def remove_state_change_listener(
            self, listener: Callable[['TaskPrerequisites', TaskPrerequisitesState], None]) -> None:
        self._state_observer.remove_listener(listener=listener)


class Task(Generic[_TR]):
    _Self = TypeVar("_Self", bound='_TaskBase')

    def __init__(
            self,
            function: Callable[[*_TPs], _TR],
            arguments: list[*_TPs] = None,
            keywords: dict[str, *_TPs] = None,
            prerequisites: list[Self] | TaskPrerequisites = None,
            priority: int = 0,
            state_change_listener: Callable[[Self, TaskState], None] = None,
            prerequisites_change_listener: Callable[[Self, TaskPrerequisitesState], None] = None,
            print_state_changes: bool = False,
    ) -> None:
        self._function = None
        self._arguments = None
        self._keywords = None
        self._prerequisites: TaskPrerequisites | None = None
        self._priority = None
        self._state: TaskState = TaskState.Creating
        self._return_value: _TR = None
        self._failing_cause: Exception | None = None
        self._state_observer = ParameterizedObserver[Self, TaskState]()
        self._prerequisites_observer = ParameterizedObserver[Self, TaskPrerequisitesState]()
        self._determined_event: Event = Event()
        self._is_printing_state_changes = print_state_changes

        self.function = function
        self.arguments = [] if arguments is None else arguments
        self.keywords = {} if keywords is None else keywords
        if prerequisites:
            self.prerequisites = prerequisites
        self.priority = priority

        if state_change_listener is not None:
            self.add_state_change_listener(listener=state_change_listener)
        if prerequisites_change_listener is not None:
            self.add_prerequisites_change_listener(listener=prerequisites_change_listener)
        if self.is_printing_state_changes:
            self._state_observer.add_listener(listener=self._print_state_change_listener)

    @property
    def function(self) -> Callable[[*_TPs], list['Task']]:
        return self._function

    @function.setter
    def function(self, new_function: Callable[[*_TPs], list['Task']]) -> None:
        if self._state is not TaskState.Creating:
            raise RuntimeError(f"'function' property can only be changed for unsubmitted tasks.")

        self._function = new_function

    @property
    def arguments(self) -> list:
        return self._arguments

    @arguments.setter
    def arguments(self, new_arguments: list) -> None:
        if self._state is not TaskState.Creating:
            raise RuntimeError(f"'arguments' property can only be changed for unsubmitted tasks.")

        self._arguments = new_arguments

    @property
    def keywords(self) -> dict[str, Any]:
        return self._keywords

    @keywords.setter
    def keywords(self, new_keywords: dict[str, Any]) -> None:
        if self._state is not TaskState.Creating:
            raise RuntimeError(f"'keywords' property can only be changed for unsubmitted tasks.")

        self._keywords = new_keywords

    @property
    def prerequisites(self) -> TaskPrerequisites | None:
        return self._prerequisites

    @prerequisites.setter
    def prerequisites(self, new_prerequisites: list['Task'] | TaskPrerequisites) -> None:
        if self._state is not TaskState.Creating:
            raise RuntimeError(f"'prerequisites' property can only be changed for unsubmitted tasks.")

        if isinstance(new_prerequisites, list):
            if not self._prerequisites:
                self._prerequisites = TaskPrerequisites()
                self._prerequisites.add_state_change_listener(self._prerequisite_state_changed)
            self._prerequisites.clear_tasks()
            self._prerequisites.add_tasks(new_tasks=new_prerequisites)

        elif isinstance(new_prerequisites, TaskPrerequisites):
            if self._prerequisites is not None:
                self._prerequisites.remove_state_change_listener(self._prerequisite_state_changed)
            self._prerequisites = new_prerequisites
            self._prerequisites.add_state_change_listener(self._prerequisite_state_changed)

        else:
            raise TypeError("'prerequisites' parameter has to be a list of Tasks or a TaskPrerequisites instance.")

    @property
    def priority(self) -> int:
        return self._priority

    @priority.setter
    def priority(self, new_priority: int) -> None:
        if self._state is not TaskState.Creating:
            raise RuntimeError(f"'priority' property can only be changed for unsubmitted tasks.")

        self._priority = new_priority

    @property
    def state(self) -> TaskState:
        return self._state

    @state.setter
    def state(self, new_state: TaskState) -> None:
        if (
                (new_state is TaskState.Creating) or
                (new_state is TaskState.Prerequisites_Unfulfilled and self._state is not TaskState.Creating) or
                (new_state is TaskState.Executable and self._state not in [TaskState.Creating,
                                                                           TaskState.Prerequisites_Unfulfilled]) or
                (new_state is TaskState.Running and self._state is not TaskState.Executable) or
                (new_state in [TaskState.Successful, TaskState.Failed] and self._state is not TaskState.Running)
        ):
            raise ValueError(f"Cannot set state to '{new_state}' from '{self._state}'")

        previous_state = self.state
        if self.prerequisites:
            self.prerequisites.lock()
        self._state = new_state
        self._state_observer.notify_listeners(self, previous_state)

        if self.state == TaskState.Running:
            self._prerequisites_observer.remove_all_listener()
            self._prerequisites_observer = None
        elif self.state in TaskState.determined_states():
            self._state_observer.remove_all_listener()
            self._state_observer = None
            self._determined_event.set()

    @property
    def return_value(self) -> _TR:
        return self._return_value

    @return_value.setter
    def return_value(self, new_return_value: Any) -> None:
        if self._state is not TaskState.Running:
            raise RuntimeError(f"'return_value' property can only be changed while task is running.")

        self._return_value = new_return_value

    @property
    def failing_cause(self) -> Exception:
        return self._failing_cause

    @failing_cause.setter
    def failing_cause(self, new_failing_cause: Exception) -> None:
        if self._state is not TaskState.Running:
            raise RuntimeError(f"'failing_cause' property can only be changed while task is running.")

        self._failing_cause = new_failing_cause

    @property
    def result(self) -> _TR:
        if self.state is TaskState.Successful:
            return self.return_value

        elif self.state is TaskState.Failed:
            raise TaskExecutionException(f"Task execution failure for task:\n{repr(self)}",
                                         task=self) from self.failing_cause

        elif self.state is TaskState.Prerequisite_Failed:
            raise TaskPrerequisiteException(f"A prerequisite task failed for task:\n{repr(self)}", task=self)

        else:
            raise RuntimeError(f"'result' property can only be accessed when the task execution finished.")

    @property
    def safe_result(self) -> Any:
        self.wait_for_result()
        return self.result

    def wait_for_result(self, timeout_seconds: float = None) -> bool:
        return self._determined_event.wait(timeout=timeout_seconds)

    @property
    def is_result_determined(self) -> bool:
        return self._determined_event.is_set()

    @property
    def is_printing_state_changes(self) -> bool:
        return self._is_printing_state_changes

    @is_printing_state_changes.setter
    def is_printing_state_changes(self, is_printing_state_changes: bool) -> None:
        self._is_printing_state_changes = is_printing_state_changes

        if self.is_printing_state_changes:
            self._state_observer.add_listener(listener=self._print_state_change_listener)
        else:
            self._state_observer.remove_listener(listener=self._print_state_change_listener)

    def _print_state_change_listener(self, _, __) -> None:
        print(f"task state changed to '{self.state}': ", self.small_repr)

    def _prerequisite_state_changed(self, _, previous_state: TaskPrerequisitesState) -> None:
        if self._prerequisites_observer is not None:
            self._prerequisites_observer.notify_listeners(self, previous_state)

    def add_state_change_listener(self, listener: Callable[[_Self, TaskState], None]) -> None:
        if self._state_observer is not None:
            self._state_observer.add_listener(listener=listener)

    def remove_state_change_listener(self, listener: Callable[[_Self, TaskState], None]) -> None:
        if self._state_observer is not None:
            self._state_observer.remove_listener(listener=listener)

    def add_prerequisites_change_listener(self, listener: Callable[[_Self, TaskPrerequisitesState], None]) -> None:
        if self._prerequisites_observer is not None:
            self._prerequisites_observer.add_listener(listener=listener)

    def remove_prerequisites_change_listener(self, listener: Callable[[_Self, TaskPrerequisitesState], None]) -> None:
        if self._prerequisites_observer is not None:
            self._prerequisites_observer.remove_listener(listener=listener)

    @property
    def small_repr(self) -> str:
        num_prerequisites = len(self.prerequisites) if self.prerequisites else 0
        num_prerequisites_fulfilled = self.prerequisites.num_fulfilled_prerequisites if self.prerequisites else 0
        value = f'{self.__class__.__name__}('
        value += f'function: {self.function.__name__}, args: {self.arguments}, kwargs: {self.keywords}, '
        value += f'prerequisites: {num_prerequisites_fulfilled}/{num_prerequisites}, state: {self.state}'
        value += f', return_value: {self.return_value}' if self.state is TaskState.Successful else ''
        value += (f', failing_cause:\n ' + ''.join(format_exception(self.failing_cause))
                  if self.state in TaskState.failed_states() else '')
        value += f')'

        return value

    def __repr__(self) -> str:
        num_prerequisites = len(self.prerequisites) if self.prerequisites else 0
        num_prerequisites_fulfilled = self.prerequisites.num_fulfilled_prerequisites if self.prerequisites else 0
        value = f'{self.__class__.__name__}('
        value += f'function: {self.function}, args: {self.arguments}, kwargs: {self.keywords}, '
        value += f'prerequisites: {num_prerequisites_fulfilled}/{num_prerequisites}, state: {self.state}, '
        value += f'return_value: {self.return_value}' if self.state is TaskState.Successful else ''
        value += f'failing_cause: {self.failing_cause}, ' if self.state is TaskState.failed_states() else ''
        value += (f'state_listeners: {len(self._state_observer)}, '
                  if self._state_observer and len(self._state_observer) > 0 else '')
        value += (f'prerequisites_listeners: {len(self._prerequisites_observer)}, '
                  if self._prerequisites_observer and len(self._prerequisites_observer) > 0 else '')
        value += f'print_state_changes: {self.is_printing_state_changes})'

        return value


class SubmissionTask(Task[list[Task]]):
    def __init__(
            self,
            processor: 'TaskProcessor',
            tasks_getter: Callable[[*_TPs], list[Task]],
            arguments: list[*_TPs] = None,
            keywords: dict[str, *_TPs] = None,
            prerequisites: list['Task'] | TaskPrerequisites = None,
            priority: int = 0,
            state_change_listener: Callable[[Self, TaskState], None] = None,
            prerequisites_change_listener: Callable[[Self, TaskPrerequisitesState], None] = None,
            print_state_changes: bool = False,
    ):
        super().__init__(
            function=self._submission_function,
            arguments=arguments,
            keywords=keywords,
            prerequisites=prerequisites,
            priority=priority,
            state_change_listener=state_change_listener,
            prerequisites_change_listener=prerequisites_change_listener,
            print_state_changes=print_state_changes,
        )

        self._processor = processor
        self._tasks_getter = tasks_getter

    def _submission_function(self, *args, **kwargs) -> list['Task']:
        tasks = self._tasks_getter(*args, **kwargs)
        self._processor.submit_tasks_async(tasks=tasks)
        return tasks

    @property
    def function(self) -> Callable[[*_TPs], list['Task']]:
        return self._function

    @function.setter
    def function(self, new_function: Callable[[*_TPs], list['Task']]) -> None:
        if self.function is None:
            self._function = new_function
            return

        message = (f"'function' property of {self.__class__.__name__} cannot be changed. Did you mean "
                   f"'tasks_getter' property?")

        raise RuntimeError(message)

    @property
    def tasks_getter(self) -> Callable[[*_TPs], list[Task]]:
        return self._tasks_getter

    @tasks_getter.setter
    def tasks_getter(self, new_getter: Callable[[*_TPs], list[Task]]) -> None:
        if self.state is not TaskState.Creating:
            raise RuntimeError(f"'function' property can only be changed for unsubmitted tasks.")

        self._tasks_getter = new_getter

    @property
    def small_repr(self) -> str:
        num_prerequisites = len(self.prerequisites) if self.prerequisites else 0
        num_prerequisites_fulfilled = self.prerequisites.num_fulfilled_prerequisites if self.prerequisites else 0
        value = f'{self.__class__.__name__}('
        value += f'tasks_getter: {self.tasks_getter.__name__}, args: {self.arguments}, kwargs: {self.keywords}, '
        value += f'prerequisites: {num_prerequisites_fulfilled}/{num_prerequisites}, state: {self.state}'
        value += f', num_tasks_created: {len(self.return_value)}' if self.state is TaskState.Successful else ''
        value += (f', failing_cause:\n ' + ''.join(format_exception(self.failing_cause))
                  if self.state in TaskState.failed_states() else '')
        value += f')'

        return value

    def __repr__(self) -> str:
        num_prerequisites = len(self.prerequisites) if self.prerequisites else 0
        num_prerequisites_fulfilled = self.prerequisites.num_fulfilled_prerequisites if self.prerequisites else 0
        value = f'{self.__class__.__name__}('
        value += f'tasks_getter: {self.tasks_getter}, args: {self.arguments}, kwargs: {self.keywords}, '
        value += f'prerequisites: {num_prerequisites_fulfilled}/{num_prerequisites}, state: {self.state}, '
        value += f'return_value: {self.return_value}' if self.state is TaskState.Successful else ''
        value += f'failing_cause: {self.failing_cause}, ' if self.state is TaskState.failed_states() else ''
        value += (f'state_listeners: {len(self._state_observer)}, '
                  if self._state_observer and len(self._state_observer) > 0 else '')
        value += (f'prerequisites_listeners: {len(self._prerequisites_observer)}, '
                  if self._prerequisites_observer and len(self._prerequisites_observer) > 0 else '')
        value += f'print_state_changes: {self.is_printing_state_changes})'

        return value


class TaskBook:
    _associated_task_state_mapping = {
        TaskPrerequisitesState.Fulfilled: TaskState.Executable,
        TaskPrerequisitesState.Unfulfilled: TaskState.Prerequisites_Unfulfilled,
        TaskPrerequisitesState.Unfulfillable: TaskState.Prerequisite_Failed,
    }

    def __init__(self):
        self._mutex = RLock()
        self.task_lists: dict[TaskState, list[Task]] = {
            TaskState.Executable: [],
            TaskState.Prerequisites_Unfulfilled: [],
        }
        self._pop_condition = Condition(self._mutex)

    def extend(self, new_tasks: list[Task]) -> None:
        with self._mutex:
            new_tasks = sorted(new_tasks, key=lambda t: t.priority, reverse=True)
            for task in new_tasks:
                self.insert(new_task=task)

    def insert(self, new_task: Task) -> None:
        with self._mutex:
            if new_task.state is not TaskState.Creating:
                raise ValueError(f"Cannot submit task with state '{new_task.state}.'")

            new_task.add_prerequisites_change_listener(self._task_prerequisites_state_changed)
            self._insert_task_into_associated_task_list(task=new_task)

    def _task_prerequisites_state_changed(self, task: Task, previous_state: TaskPrerequisitesState) -> None:
        with self._mutex:
            self.task_lists[self._associated_task_state_mapping[previous_state]].remove(task)
            self._insert_task_into_associated_task_list(task=task)

    def _insert_task_into_associated_task_list(self, task: Task) -> None:
        with self._mutex:
            self._change_task_state_accordingly(task=task)

            if not task.is_result_determined:
                insort(self.task_lists[task.state], task, key=lambda t: -t.priority)
            if self.is_executable_task_available:
                self._pop_condition.notify(1)

    def _change_task_state_accordingly(self, task: Task):
        with self._mutex:
            if task.prerequisites:
                task.state = self._associated_task_state_mapping[task.prerequisites.state]
            else:
                task.state = TaskState.Executable

    def pop_next_executable_task(self, timeout_seconds: float = 5.0) -> Task | None:
        with self._pop_condition:
            is_task_available = self._pop_condition.wait_for(lambda: self.is_executable_task_available,
                                                             timeout=timeout_seconds)

            if is_task_available:
                task = self.task_lists[TaskState.Executable].pop(0)
                task.remove_prerequisites_change_listener(self._task_prerequisites_state_changed)
                return task
            else:
                return None

    @property
    def is_executable_task_available(self) -> bool:
        with self._mutex:
            return len(self.task_lists[TaskState.Executable]) > 0


class TaskProcessor:
    # TODO add administration and monitoring thread for workers
    #  => automatic restarts when stopped
    #  => timeout for tasks in task book with unfulfilled prerequisites
    #  => detect infinity loops of tasks (execution timeout)
    #  ...
    def __init__(
            self,
            num_workers: int = 4,
            are_daemon_workers: bool = True,
    ):
        # Task books
        self._task_book: TaskBook = TaskBook()
        self._task_submitter_task_book = TaskBook()

        # workers
        self._workers: list[TaskWorker] = []
        self._task_submitter: TaskWorker = TaskWorker(
            idx='task_creation', task_book=self._task_submitter_task_book, is_daemon=are_daemon_workers)

        # locks
        self._workers_list_lock = Lock()

        # set initial values
        self._are_daemon_workers = are_daemon_workers
        self.num_workers = num_workers

    @property
    def num_workers(self) -> int:
        return len(self._workers)

    @num_workers.setter
    def num_workers(self, value: int) -> None:
        self._validate_is_valid_thread()
        current_num_workers = self.num_workers
        if current_num_workers < value:
            for _ in range(value - current_num_workers):
                self._add_new_worker()

        elif current_num_workers > value:
            for _ in range(current_num_workers - value):
                self._remove_worker()

    def _add_new_worker(self) -> None:
        with self._workers_list_lock:
            idx = self._lowest_free_id()
            worker = TaskWorker(idx=idx, task_book=self._task_book, is_daemon=self._are_daemon_workers)

            self._workers.append(worker)
            self._workers.sort(key=lambda w: w.idx)

    def _remove_worker(self):
        with self._workers_list_lock:
            worker = self._workers.pop(-1)
            worker.__del__()
            del worker

    def _lowest_free_id(self) -> int:
        """
        :return: Lowest free id for a new worker. Possible ids starting at 1.
        """
        possible_ids = {i for i in range(1, len(self._workers) + 2)}
        used_ids = set([worker.idx for worker in self._workers])
        free_ids = possible_ids - used_ids
        return sorted(list(free_ids))[0]

    def submit_groups_async(self, groups: TaskGroupCollection) -> None:
        self.submit_tasks_async(groups.unsubmitted_tasks)

    def submit_tasks_async(self, tasks: list[Task]) -> None:
        other_tasks, submission_tasks = self._split_submission_tasks(tasks=tasks)

        if len(other_tasks) > 0:
            self._validate_is_valid_thread()

        self._task_submitter_task_book.extend(new_tasks=submission_tasks)
        self._task_book.extend(new_tasks=other_tasks)

    def submit_task_async(self, task: Task) -> None:
        if isinstance(task, SubmissionTask):
            self._task_submitter_task_book.insert(new_task=task)
        else:
            self._validate_is_valid_thread()
            self._task_book.insert(new_task=task)

    def submit_groups_sync(self, groups: TaskGroupCollection) -> None:
        self.submit_tasks_sync(groups.unsubmitted_tasks)

    def submit_tasks_sync(self, tasks: list[Task]) -> None:
        self._validate_is_valid_thread()

        other_tasks, submission_tasks = self._split_submission_tasks(tasks=tasks)

        self._task_submitter_task_book.extend(new_tasks=submission_tasks)
        self._task_book.extend(new_tasks=other_tasks)

        self.wait_until_task_results_have_been_determined(tasks=tasks)

    def submit_task_sync(self, task: Task) -> Any:
        self._validate_is_valid_thread()

        if isinstance(task, SubmissionTask):
            self._task_submitter_task_book.insert(new_task=task)
            task.wait_for_result()
            return task.state == TaskState.Successful
        else:
            self._task_book.insert(new_task=task)
            return task.safe_result

    def _validate_is_valid_thread(self):
        current_thread = threading.current_thread()
        associated_worker = [worker for worker in self._workers if worker.is_worker_thread(thread=current_thread)]
        if len(associated_worker) > 0:
            task = associated_worker[0].current_task
            message = ("Cannot submit new tasks because you either try to add new tasks from a running Task or you "
                       "try to submit a SubmissionTask synchronously. "
                       "You can submit new tasks from a running task by using a SubmissionTask instance and submitting"
                       "it asynchronously.")
            raise TaskExecutionException(message=message, task=task)

    @classmethod
    def _split_submission_tasks(cls, tasks: list[Task]) -> tuple[list[Task], list[SubmissionTask]]:
        submission_tasks = []
        other_tasks = []
        for task in tasks:
            if isinstance(task, SubmissionTask):
                submission_tasks.append(task)
            else:
                other_tasks.append(task)

        return other_tasks, submission_tasks

    @staticmethod
    def wait_until_task_results_have_been_determined(tasks: list[Task], timeout_seconds: float = None) -> bool:
        barrier = TaskBarrier(tasks=tasks)
        return barrier.wait_until_all_task_results_have_been_determined(timeout_seconds=timeout_seconds)

    def __del__(self) -> None:
        self.num_workers = 0
        del self._task_submitter


class TaskWorkerState(StrEnum):
    """ The execution status of a worker. """

    Created = auto()
    """ Just created the worker instance. The underlying thread is not ready to process tasks yet. """
    Restarting = auto()
    """ worker is currently recreating and starting the underlying thread. """
    Waiting = auto()
    """ worker is currently waiting for a new task. """
    Processing = auto()
    """ worker is currently processing a task """
    Stopping = auto()
    """ worker is stopping the underlying thread. """
    Stopped = auto()
    """ worker stopped the underlying thread and now cannot process any tasks. """
    Terminate = auto()
    """ worker is terminated and this instance will be destroyed anytime. """


class TaskWorker:
    def __init__(self, idx: Immutable, task_book: TaskBook, is_daemon: bool | None = None):
        self._idx = idx
        self._name = f'worker_{idx}'
        self._task_book = task_book
        self._is_daemon = is_daemon
        self._current_task: Task | None
        self._thread: Thread

        self._state = TaskWorkerState.Created
        self._start()

    def _process_task_list(self) -> None:
        while self.state not in [TaskWorkerState.Stopping, TaskWorkerState.Terminate]:
            self._state = TaskWorkerState.Waiting
            task = self._current_task = self._task_book.pop_next_executable_task(timeout_seconds=5)

            if task is None:
                continue

            try:
                self._state = TaskWorkerState.Processing
                task.state = TaskState.Running
                task.return_value = task.function(*task.arguments, **task.keywords)
                task.state = TaskState.Successful
            except Exception as e:
                task.failing_cause = e
                task.state = TaskState.Failed
            finally:
                self._current_task = None

        if self.state is TaskWorkerState.Stopping:
            self._state = TaskWorkerState.Stopped

    @property
    def idx(self) -> Immutable:
        return self._idx

    @property
    def state(self) -> TaskWorkerState:
        return self._state

    @property
    def current_task(self) -> Task:
        return self._current_task

    def stop(self, block=False, timeout_seconds: float = None):
        self._state = TaskWorkerState.Stopping

        if not block:
            return

        if self._thread.is_alive():
            self._thread.join(timeout=timeout_seconds)

    def restart(self) -> None:
        if self.state is not TaskWorkerState.Stopped:
            raise RuntimeError(f"Only 'stopped' workers can be restarted. Current state is {self.state}")

        self._state = TaskWorkerState.Restarting
        self._start()

    def _start(self) -> None:
        self._thread: Thread = Thread(
            target=self._process_task_list,
            name=self._name,
            daemon=self._is_daemon
        )
        self._thread.start()

    def __del__(self) -> None:
        self._state = TaskWorkerState.Terminate
        self._task_book = None

    def is_worker_thread(self, thread: Thread) -> bool:
        return thread is self._thread
