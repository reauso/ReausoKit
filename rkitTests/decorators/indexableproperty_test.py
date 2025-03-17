from unittest import TestCase

from rkit.decorators.indexableproperty import IndexableProperty


class IndexablePropertyUser:
    def __init__(self, array):
        self._my_list = array

    @IndexableProperty
    def my_property(self, item):
        return self._my_list[item]

    @my_property.itemsetter
    def my_property(self, key, value):
        self._my_list[key] = value


class IndexablePropertyTests(TestCase):
    def test_get_property__Always__ReturnsIndexablePropertyObject(self):
        # Arrange
        user = IndexablePropertyUser([i for i in range(100)])

        # Act
        actual = user.my_property

        # Assert
        self.assertIsInstance(actual, IndexableProperty)

    def test_set_property__Always__RaisesAttributeError(self):
        # Arrange
        user = IndexablePropertyUser([i for i in range(100)])

        # Act & Act
        with self.assertRaises(AttributeError):
            user.my_property = []

    def test_getitem__All__ReturnsCompleteList(self):
        # Arrange
        user = IndexablePropertyUser([i for i in range(100)])

        # Act
        actual = user.my_property[:]

        # Assert
        self.assertIsInstance(actual, list)
        self.assertListEqual(actual, [i for i in range(100)])

    def test_getitem__Sliced__ReturnsCompleteList(self):
        # Arrange
        user = IndexablePropertyUser([i for i in range(100)])

        # Act
        actual = user.my_property[10:40]

        # Assert
        self.assertIsInstance(actual, list)
        self.assertListEqual(actual, [i for i in range(10, 40)])

    def test_setitem__All__ReturnsCompleteList(self):
        # Arrange
        user = IndexablePropertyUser([i for i in range(100)])

        # Act
        user.my_property[:] = [1 for _ in range(100)]

        # Assert
        self.assertListEqual(user._my_list, [1 for _ in range(100)])

    def test_setitem__Sliced__ReturnsCompleteList(self):
        # Arrange
        user = IndexablePropertyUser([i for i in range(100)])

        # Act
        user.my_property[10:40] = [1 for _ in range(10, 40)]

        # Assert
        self.assertListEqual(user._my_list, [1 if 10 <= i < 40 else i for i in range(100)])