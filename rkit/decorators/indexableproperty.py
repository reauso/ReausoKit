from collections.abc import Callable
from typing import TypeVar, Generic, Any

O = TypeVar('O')
T = TypeVar('T')
R = TypeVar('R')


class IndexableProperty(Generic[O, T, R]):
    """
    An instance property which can be accessed and modified by pythons __getitem__ and
    __setitem__ functions. Meant to be used as decorator function.
    Implements similar interface as pythons property inbuilt function except that getter function is
    called itemgetter and setter function is called itemsetter.
    See pythons property inbuilt function for more information.
    """

    def __init__(
            self,
            fget: Callable[[O, T], R] = None,
            fset: Callable[[O, T, R], None] = None,
            fdel: Callable[[O, T], None] = None,
            pdel: Callable[[O], None] = None,
            doc: str = None
    ):
        """
        Returns an indexable property attribute.
        The advantage compared to property is, that an indexable property does not provide direct access
        to an underlying attribute and therefore favours the enclosure principle to produce cleaner code.
        E.g. if the underlying data structure is a list, you do not have access to the list object but
        instead access to the values of the list.

        :param fget: is a function for accessing attribute value(s). It's parameters have to be as __getitem__
        function.
        :param fset: is a function for setting attribute value(s). It's parameters have to be as __setitem__
        function.
        :param pdel: is a function for deleting attribute value(s). It's parameters have to be as __delitem__
        function.
        :param fdel: is a function for deleting the attribute.
        :param doc: creates a docstring for the attribute.
        """
        self._fget: Callable[[O, T], R] = fget
        self._fset: Callable[[O, T, R], None] = fset
        self._fdel: Callable[[O, T], None] = fdel
        self._pdel: Callable[[O], None] = pdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        # self.__doc__ = doc
        self._owner = None
        self._name = ''

        self._instance: O = None

    def __set_name__(self, owner, name):
        self._owner = owner
        self._name = name

    def __get__(self, instance: O, owner):
        if instance is None:
            return self
        else:
            self._instance = instance

        if self._fget is None:
            raise AttributeError(
                f'IndexableProperty {self._name!r} of {type(instance).__name__!r} object has no getter'
            )
        return self

    def __getitem__(self, item: T) -> R:
        if self._fget is None:
            message = f'IndexableProperty {self._name!r} of {type(self._instance).__name__!r} object has no item getter'
            raise AttributeError(message)
        return self._fget(self._instance, item)

    def __setitem__(self, key: T, value: R) -> None:
        if self._fset is None:
            raise AttributeError(
                f'IndexableProperty {self._name!r} of {type(self._instance).__name__!r} object has no item setter'
            )
        self._fset(self._instance, key, value)

    def __delitem__(self, key: T) -> None:
        if self._fdel is None:
            raise AttributeError(
                f'IndexableProperty {self._name!r} of {type(self._instance).__name__!r} object has no item deleter'
            )
        self._fdel(self._instance, key)

    def __delete__(self, obj: O) -> None:
        if self._pdel is None:
            raise AttributeError(
                f'IndexableProperty {self._name!r} of {type(obj).__name__!r} object has no deleter'
            )
        self._pdel(obj)

    def itemgetter(self, fget: Callable[[Any, T], R]):
        """
        Defines the __getitem__ function for this indexable property.
        :param fget: A function that corresponds with the __getitem__ parameter list.
        :return: The indexable property.
        """
        prop = type(self)(fget, self._fset, self._fdel, self._pdel, self.__doc__)

        return prop

    def itemsetter(self, fset: Callable[[Any, T, R], None]):
        """
        Defines the __setitem__ function for this indexable property.
        :param fset: A function that corresponds with the __setitem__ parameter list.
        :return: The indexable property.
        """
        prop = type(self)(self._fget, fset, self._fdel, self._pdel, self.__doc__)

        return prop

    def itemdeleter(self, fdel: Callable[[Any, T], None]):
        """
        Defines the __delitem__ function for this indexable property.
        :param fdel: A function that corresponds with the __delitem__ parameter list.
        :return: The indexable property.
        """
        prop = type(self)(self._fget, self._fset, fdel, self._pdel, self.__doc__)

        return prop

    def deleter(self, pdel: Callable[[O], None]):
        """
        Defines the __del__ function for this indexable property.
        :param pdel: A function that corresponds with the __del__ parameter list.
        :return: The indexable property.
        """
        prop = type(self)(self._fget, self._fset, self._fdel, pdel, self.__doc__)
        prop._name = self._name
        return prop
