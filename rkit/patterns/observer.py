from collections.abc import Callable
from typing import Generic, Any, TypeVarTuple


Ts = TypeVarTuple('Ts')


class ParameterizedObserver(Generic[*Ts]):
    """
    An observer that holds listener callables following the given generic pattern of parameter types.
    E.g. a ParameterizedObserver[int] will only accept callables with one int type parameter as listener.
    """

    def __init__(self):
        self._listeners: set[Callable[[*Ts], object]] = set()

    def add_listener(self, listener: Callable[[*Ts], Any]) -> bool:
        """
        Register a callable as listener.
        :param listener: The callable function.
        :returns True if the listener has been newly added. False if the listener is already registered.
        """
        is_not_registered = listener not in self._listeners
        self._listeners.add(listener)
        return is_not_registered

    def remove_listener(self, listener: Callable[[*Ts], Any]) -> bool:
        """
        Remove a callable from the registered listeners list.
        :param listener: The callable function.
        :return: True, if a registered listener actually has been removed from the list of listeners.
        """
        try:
            self._listeners.remove(listener)
            return True
        except KeyError:
            return False

    def remove_all_listener(self) -> None:
        """
        Remove all listeners.
        """
        self._listeners.clear()

    @property
    def listeners(self) -> set[Callable[[*Ts], Any]]:
        return set(self._listeners)

    def notify_listeners(self, *args: *Ts) -> None:
        """
        Notify all registered listeners with the given parameter arguments.
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
