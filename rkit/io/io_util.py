from __future__ import annotations

import os

import glob
from typing import List


def files_in_directory(directory_path: os.PathLike | str, file_patterns: str = None, recursive: bool = False) -> List:
    """
    Returns all files from a specific directory.
    :param directory_path: Path to the directory.
    :param file_patterns: One or more file patterns to search for.
    :param recursive: If True searches in all subdirectories.
    :return: A list containing all files from the directory.
    """
    if file_patterns is None:
        file_patterns = ['**']
    elif not isinstance(file_patterns, list):
        file_patterns = [file_patterns]

    files = []
    for pattern in file_patterns:
        files.extend(glob.glob(os.path.join(directory_path, pattern), recursive=recursive))

    return files
