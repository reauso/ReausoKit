def list_product(l: list, start: float = 1.0) -> float:
    """
    Calculates the product of all elements in the given list, starting with an initial value.

    :param l: A list of numerical values to be multiplied.
    :param start: The initial value to start the multiplication (default is 1.0).
    :return: The final product as a float.
    """
    for entry in l:
        start *= entry

    return start


def list_quotient(l: list, start: float = 1.0) -> float:
    """
    Calculates the quotient by successively dividing an initial value by each element in the given list.

    :param l: A list of numerical values used as divisors.
    :param start: The initial value to be divided (default is 1.0).
    :return: The final quotient as a float.
    :raises ZeroDivisionError: If any element in the list is zero.
    """
    for entry in l:
        start /= entry

    return start
