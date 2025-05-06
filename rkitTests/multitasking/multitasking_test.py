from unittest.mock import patch, MagicMock, create_autospec

from parameterized import parameterized

from rkit.design_patterns import ParameterizedObserver
from rkit.multitasking import TaskState, Task, TaskProcessor
from rkit.multitasking.multitasking import TaskWorker
from rkit.unittesting import ExtendedTestCase


class TaskTests(ExtendedTestCase):
    @parameterized.expand([[state] for state in TaskState])
    def test_state_setter__SetStateToCreated__RaisedValueError(self, initial_state: TaskState):
        # Arrange
        task = Task(function=MagicMock())
        task._state = initial_state

        # Act & Assert
        regex = r"Cannot set state to 'creating' from *."
        with self.assertRaisesRegex(expected_regex=regex, expected_exception=ValueError):
            task.state = TaskState.Creating

    @parameterized.expand([[state] for state in (set(TaskState) - {TaskState.Creating})])
    def test_state_setter__SetStateToPrerequisitesUnfulfilledFromInvalid__RaisedValueError(self, initial_state: TaskState):
        # Arrange
        task = Task(function=MagicMock())
        task._state = initial_state

        # Act & Assert
        regex = r"Cannot set state to 'prerequisites_unfulfilled' from *."
        with self.assertRaisesRegex(expected_regex=regex, expected_exception=ValueError):
            task.state = TaskState.Prerequisites_Unfulfilled

    def test_state_setter__SetStateToPrerequisitesUnfulfilledFromCreated__ChangedState(self):
        # Arrange
        task = Task(function=MagicMock())
        task._state = TaskState.Creating

        # Act
        task.state = TaskState.Prerequisites_Unfulfilled

        # Assert
        expected = TaskState.Prerequisites_Unfulfilled
        self.assertEqual(expected, task._state)

    @parameterized.expand([[state] for state in (
            set(TaskState) - {TaskState.Creating, TaskState.Prerequisites_Unfulfilled})])
    def test_state_setter__SetStateToExecutableFromInvalid__RaisedValueError(self, initial_state: TaskState):
        # Arrange
        task = Task(function=MagicMock())
        task._state = initial_state

        # Act & Assert
        regex = r"Cannot set state to 'executable' from *."
        with self.assertRaisesRegex(expected_regex=regex, expected_exception=ValueError):
            task.state = TaskState.Executable

    def test_state_setter__SetStateToExecutableFromCreated__ChangedState(self):
        # Arrange
        task = Task(function=MagicMock())
        task._state = TaskState.Creating

        # Act
        task.state = TaskState.Executable

        # Assert
        expected = TaskState.Executable
        self.assertEqual(expected, task._state)

    def test_state_setter__SetStateToExecutableFromPrerequisitesUnfulfilled__ChangedState(self):
        # Arrange
        task = Task(function=MagicMock())
        task._state = TaskState.Prerequisites_Unfulfilled

        # Act
        task.state = TaskState.Executable

        # Assert
        expected = TaskState.Executable
        self.assertEqual(expected, task._state)

    @parameterized.expand([[state] for state in (set(TaskState) - {TaskState.Executable})])
    def test_state_setter__SetStateToRunningFromInvalid__RaisedValueError(self, initial_state: TaskState):
        # Arrange
        task = Task(function=MagicMock())
        task._state = initial_state

        # Act & Assert
        regex = r"Cannot set state to 'running' from *."
        with self.assertRaisesRegex(expected_regex=regex, expected_exception=ValueError):
            task.state = TaskState.Running

    def test_state_setter__SetStateToSubmittedFromSubmitted__ChangedState(self):
        # Arrange
        task = Task(function=MagicMock())
        task._state = TaskState.Executable

        # Act
        task.state = TaskState.Running

        # Assert
        expected = TaskState.Running
        self.assertEqual(expected, task._state)

    @parameterized.expand([[state] for state in (set(TaskState) - {TaskState.Running})])
    def test_state_setter__SetStateToSuccessfulFromInvalid__RaisedValueError(self, initial_state: TaskState):
        # Arrange
        task = Task(function=MagicMock())
        task._state = initial_state

        # Act & Assert
        regex = r"Cannot set state to 'successful' from *."
        with self.assertRaisesRegex(expected_regex=regex, expected_exception=ValueError):
            task.state = TaskState.Successful

    def test_state_setter__SetStateToSuccessfulFromRunning__ChangedState(self):
        # Arrange
        task = Task(function=MagicMock())
        task._state = TaskState.Running

        # Act
        task.state = TaskState.Successful

        # Assert
        expected = TaskState.Successful
        self.assertEqual(expected, task._state)

    @parameterized.expand([[state] for state in (set(TaskState) - {TaskState.Running})])
    def test_state_setter__SetStateToSuccessfulFromInvalid__RaisedValueError(self, initial_state: TaskState):
        # Arrange
        task = Task(function=MagicMock())
        task._state = initial_state

        # Act & Assert
        regex = r"Cannot set state to 'failed' from *."
        with self.assertRaisesRegex(expected_regex=regex, expected_exception=ValueError):
            task.state = TaskState.Failed

    def test_state_setter__SetStateToFailedFromRunning__ChangedState(self):
        # Arrange
        task = Task(function=MagicMock())
        task._state = TaskState.Running

        # Act
        task.state = TaskState.Failed

        # Assert
        expected = TaskState.Failed
        self.assertEqual(expected, task._state)

    @patch.object(ParameterizedObserver, ParameterizedObserver.notify_listeners.__name__)
    def test_state_setter__StateChange__CalledNotifyOfStateObserver(self, notify_mock: MagicMock):
        # Arrange
        task = Task(function=MagicMock())
        task._state = TaskState.Executable

        # Act
        task.state = TaskState.Running

        # Assert
        notify_mock.assert_called_once_with(task, TaskState.Executable)


class TaskProcessorTests(ExtendedTestCase):
    def test__lowest_free_id__NoWorker__ReturnedOne(self):
        # Arrange
        processor = TaskProcessor(num_workers=0)

        # Act
        actual = processor._lowest_free_id()

        # Assert
        expected = 1
        self.assertEqual(expected, actual)

    def test__lowest_free_id__ContinuousWorkerIds__ReturnedNumberOfWorkersPlusOne(self):
        # Arrange
        processor = TaskProcessor()
        processor._workers = [
            create_autospec(TaskWorker, idx=1, instance=True),
            create_autospec(TaskWorker, idx=2, instance=True),
            create_autospec(TaskWorker, idx=3, instance=True),
            create_autospec(TaskWorker, idx=4, instance=True),
        ]

        # Act
        actual = processor._lowest_free_id()

        # Assert
        expected = 5
        self.assertEqual(expected, actual)

    def test__lowest_free_id__NoContinuousWorkerIds__ReturnedMissingWorkerId(self):
        # Arrange
        processor = TaskProcessor()
        processor._workers = [
            create_autospec(TaskWorker, idx=1, instance=True),
            create_autospec(TaskWorker, idx=2, instance=True),
            create_autospec(TaskWorker, idx=6, instance=True),
            create_autospec(TaskWorker, idx=16, instance=True),
        ]

        # Act
        actual = processor._lowest_free_id()

        # Assert
        expected = 3
        self.assertEqual(expected, actual)