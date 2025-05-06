from collections.abc import Callable

from typing import TypeVar, Generic, TypeVarTuple

_T = TypeVar('_T')
_Ts = TypeVarTuple('_Ts')


class ParameterizedObserver(Generic[*_Ts]):  # TODO set to python 3.11
    """
    An observer that holds listener callables following the given generic pattern of parameter types.
    E.g. a ParameterizedObserver[int] will only accept callables with one int type parameter as listener.
    """

    def __init__(self):
        self._listeners: list[Callable[[*_Ts], object]] = []

    def add_listener(self, listener: Callable[[*_Ts], object]) -> None:
        """
        Registers a callable as listener.
        :param listener: The callable function.
        """
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[*_Ts], object]) -> bool:
        """
        Removes all entries of a callable from the registered listeners list.
        :param listener: The callable function.
        :return: True, if any registered listener actually was removed from the list of listeners.
        """
        initial_length = len(self._listeners)
        self._listeners = [func for func in self._listeners if func != listener]
        return initial_length != len(self._listeners)

    def remove_all_listener(self) -> None:
        """
        Removes all listeners.
        """
        self._listeners.clear()

    def notify_listeners(self, *args: *_Ts) -> None:
        """
        Notifies all registered listeners with the given parameter arguments.
        :param args: The parameter arguments to pass to the listener functions.
        """
        for listener in self._listeners:
            listener(*args)

    def __len__(self) -> int:
        return len(self._listeners)

    def __contains__(self, item):
        return item in self._listeners

    def __eq__(self, other):
        if isinstance(other, ParameterizedObserver):
            return self._listeners == other._listeners
        else:
            return False
