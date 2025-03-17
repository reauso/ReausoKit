def replace_multiple(s: str, replacements: dict[str, str]) -> str:
    """
    Replaces multiple substrings in a given string based on a dictionary of replacements.

    :param s: The input string in which replacements will be made.
    :param replacements: A dictionary where keys are substrings to be replaced,
                         and values are the corresponding replacement strings.
    :return: The modified string with all specified replacements applied.

    Example:
        >>> replace_multiple("hello world", {"hello": "hi", "world": "everyone"})
        'hi everyone'
    """
    for old, new in replacements.items():
        s = s.replace(old, new)
    return s
