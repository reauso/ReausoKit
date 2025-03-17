from unittest import TestCase
from unittest.mock import patch, MagicMock

from rkit.patterns.observer import ParameterizedObserver


class ParameterizedObserverTests(TestCase):
    @staticmethod
    def listener1a():
        pass

    @staticmethod
    def listener1b():
        pass

    @staticmethod
    def listener1c():
        pass

    @staticmethod
    def listener2a(a: int, b: int, c: str):
        pass

    @staticmethod
    def listener2b(a: int, b: int, c: str):
        pass

    @staticmethod
    def listener2c(a: int, b: int, c: str):
        pass

    def test_construction__AlwaysHas__EmptyListenerSet(self):
        # Arrange & Act
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver[int, int, str]()

        # Assert
        self.assertSetEqual(observer1._listeners, set())
        self.assertSetEqual(observer2._listeners, set())

    def test_add_listener__EmptyListenerSet__AddCallableToListenerSet(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver[int, int, str]()

        # Act
        observer1.add_listener(self.listener1a)
        observer2.add_listener(self.listener2a)

        # Assert
        self.assertEqual(len(observer1._listeners), 1)
        self.assertEqual(len(observer2._listeners), 1)
        self.assertIn(self.listener1a, observer1._listeners)
        self.assertIn(self.listener2a, observer2._listeners)

    def test_add_listener__CallableIsNotRegistered__AddCallableToListenerSet(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver[int, int, str]()

        observer1._listeners = {self.listener1a}
        observer2._listeners = {self.listener2a, self.listener2b}

        # Act
        observer1.add_listener(self.listener1b)
        observer2.add_listener(self.listener2c)

        # Assert
        self.assertEqual(len(observer1._listeners), 2)
        self.assertEqual(len(observer2._listeners), 3)
        self.assertSetEqual(observer1._listeners, {self.listener1a, self.listener1b})
        self.assertSetEqual(observer2._listeners, {self.listener2a, self.listener2b, self.listener2c})

    def test_add_listener__CallableIsNotRegistered__ReturnTrue(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver[int, int, str]()

        observer1._listeners = set()
        observer2._listeners = {self.listener2a, self.listener2b}

        # Act
        actual1 = observer1.add_listener(self.listener1a)
        actual2 = observer2.add_listener(self.listener2c)

        # Assert
        self.assertIn(self.listener1a, observer1._listeners)
        self.assertIn(self.listener2c, observer2._listeners)
        self.assertTrue(actual1)
        self.assertTrue(actual2)

    def test_add_listener__CallableIsRegistered__NoChangeForListenerSet(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver[int, int, str]()

        observer1._listeners = {self.listener1a}
        observer2._listeners = {self.listener2a, self.listener2b}

        # Act
        observer1.add_listener(self.listener1a)
        observer2.add_listener(self.listener2a)

        # Assert
        self.assertEqual(len(observer1._listeners), 1)
        self.assertEqual(len(observer2._listeners), 2)
        self.assertSetEqual(observer1._listeners, {self.listener1a})
        self.assertSetEqual(observer2._listeners, {self.listener2a, self.listener2b})

    def test_add_listener__CallableIsRegistered__ReturnFalse(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver[int, int, str]()

        observer1._listeners = {self.listener1a}
        observer2._listeners = {self.listener2a, self.listener2b}

        # Act
        actual1 = observer1.add_listener(self.listener1a)
        actual2 = observer2.add_listener(self.listener2b)

        # Assert
        self.assertIn(self.listener1a, observer1._listeners)
        self.assertIn(self.listener2b, observer2._listeners)
        self.assertFalse(actual1)
        self.assertFalse(actual2)

    def test_remove_listener__CallableIsRegistered__RemoveCallableFromListenerSet(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver[int, int, str]()

        observer1._listeners = {self.listener1a}
        observer2._listeners = {self.listener2a, self.listener2b}

        # Act
        observer1.remove_listener(self.listener1a)
        observer2.remove_listener(self.listener2a)

        # Assert
        self.assertEqual(len(observer1._listeners), 0)
        self.assertEqual(len(observer2._listeners), 1)
        self.assertSetEqual(observer1._listeners, set())
        self.assertSetEqual(observer2._listeners, {self.listener2b})

    def test_remove_listener__CallableIsRegistered__ReturnTrue(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver[int, int, str]()

        observer1._listeners = {self.listener1a}
        observer2._listeners = {self.listener2a, self.listener2b}

        # Act
        actual1 = observer1.remove_listener(self.listener1a)
        actual2 = observer2.remove_listener(self.listener2a)

        # Assert
        self.assertNotIn(self.listener1a, observer1._listeners)
        self.assertNotIn(self.listener2a, observer1._listeners)
        self.assertTrue(actual1)
        self.assertTrue(actual2)

    def test_remove_listener__CallableIsNotRegistered__UnchangedListenerSet(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver[int, int, str]()

        observer1._listeners = {self.listener1a}
        observer2._listeners = {self.listener2a, self.listener2b}

        # Act
        observer1.remove_listener(self.listener1c)
        observer2.remove_listener(self.listener2c)

        # Assert
        self.assertEqual(len(observer1._listeners), 1)
        self.assertEqual(len(observer2._listeners), 2)
        self.assertSetEqual(observer1._listeners, {self.listener1a})
        self.assertSetEqual(observer2._listeners, {self.listener2a, self.listener2b})

    def test_remove_listener__CallableIsNotRegistered__ReturnFalse(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver[int, int, str]()

        observer1._listeners = {self.listener1a}
        observer2._listeners = {self.listener2a, self.listener2b}

        # Act
        actual1 = observer1.remove_listener(self.listener1b)
        actual2 = observer2.remove_listener(self.listener2c)

        # Assert
        self.assertNotIn(self.listener1b, observer1._listeners)
        self.assertNotIn(self.listener2c, observer1._listeners)
        self.assertFalse(actual1)
        self.assertFalse(actual2)

    def test_remove_all_listener__Always__EmptyListenerSet(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver[int, int, str]()

        observer1._listeners = set()
        observer2._listeners = {self.listener2a, self.listener2b}

        # Act & Assert
        observer1.remove_all_listener()
        observer2.remove_all_listener()

        # Assert
        self.assertEqual(len(observer1._listeners), 0)
        self.assertEqual(len(observer2._listeners), 0)

    @patch(f'{listener1c.__module__}.ParameterizedObserverTests.{listener1c.__name__}')
    @patch(f'{listener1b.__module__}.ParameterizedObserverTests.{listener1b.__name__}')
    @patch(f'{listener1a.__module__}.ParameterizedObserverTests.{listener1a.__name__}')
    def test_notify_listeners__NoParams__CallsAllListeners(
            self, mock_1a: MagicMock, mock_1b: MagicMock, mock_1c: MagicMock):
        # Arrange
        observer1 = ParameterizedObserver()
        observer1._listeners = {self.listener1a, self.listener1b}

        # Act
        # noinspection PyTypeChecker
        observer1.notify_listeners()

        # Assert
        mock_1a.assert_called_once_with()
        mock_1b.assert_called_once_with()
        mock_1c.assert_not_called()

    @patch(f'{listener2c.__module__}.ParameterizedObserverTests.{listener2c.__name__}')
    @patch(f'{listener2b.__module__}.ParameterizedObserverTests.{listener2b.__name__}')
    @patch(f'{listener2a.__module__}.ParameterizedObserverTests.{listener2a.__name__}')
    def test_notify_listeners__WithParams__CallsAllListenersWithParams(
            self, mock_2a: MagicMock, mock_2b: MagicMock, mock_2c: MagicMock):
        # Arrange
        observer2 = ParameterizedObserver[int, int, str]()

        observer2._listeners = {self.listener2a, self.listener2b}

        # Act
        observer2.notify_listeners(5, 2, 'test')

        # Assert
        mock_2a.assert_called_once_with(5, 2, 'test')
        mock_2b.assert_called_once_with(5, 2, 'test')
        mock_2c.assert_not_called()

    def test_eq__BothEmptyListenerSet__ReturnsTrue(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver()

        observer1._listeners = set()
        observer2._listeners = set()

        # Act & Assert
        equality = observer1 == observer2

        # Assert
        self.assertTrue(equality)

    def test_eq__EqualNonEmptyListenerSet__ReturnsTrue(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver()

        observer1._listeners = {self.listener1a, self.listener1b}
        observer2._listeners = {self.listener1b, self.listener1a}

        # Act & Assert
        equality = observer1 == observer2

        # Assert
        self.assertTrue(equality)

    def test_eq__UnequalNonEmptyListenerSet__ReturnsFalse(self):
        # Arrange
        observer1 = ParameterizedObserver()
        observer2 = ParameterizedObserver()

        observer1._listeners = {self.listener1b, self.listener1a}
        observer2._listeners = {self.listener1c, self.listener1b}

        # Act & Assert
        equality = observer1 == observer2

        # Assert
        self.assertFalse(equality)
