import unittest
from typing import List
from unittest.mock import patch, MagicMock, call

from parameterized import parameterized

from rkit.io.io_util import files_in_directory


class IOUtilTest(unittest.TestCase):

    @patch('glob.glob')
    def test_files_in_directory__default__CallsGlobOnce(
            self,
            mock_function: MagicMock,
    ):
        # Arrange
        directory_path = './Test/'

        # Act
        files_in_directory(directory_path=directory_path)

        # Assert
        mock_function.assert_called_once_with('./Test/**', recursive=False)

    @parameterized.expand([[[]], [['a.txt']], [['a.txt', 'b.mp3']]])
    @patch('glob.glob')
    def test_files_in_directory__default__ReturnsMockedData(
            self,
            data,
            mock_function: MagicMock,
    ):
        # Arrange
        directory_path = './Test/'
        length = len(data)
        mock_function.return_value = data

        # Act
        files = files_in_directory(directory_path=directory_path)

        # Assert
        self.assertIsInstance(files, List)
        self.assertEqual(len(files), length)
        self.assertListEqual(files, data)

    @patch('glob.glob')
    def test_files_in_directory__with_recursion__CallsGlobWithRecursion(
            self,
            mock_function: MagicMock,
    ):
        # Arrange
        directory_path = './Test/'

        # Act
        files_in_directory(directory_path=directory_path, recursive=True)

        # Assert
        mock_function.assert_called_once_with('./Test/**', recursive=True)

    @parameterized.expand([['.mp3'], ['*.txt'], ['**.wav']])
    @patch('glob.glob')
    def test_files_in_directory__OnePattern__CallsGlobOnce(
            self,
            pattern,
            mock_function: MagicMock,
    ):
        # Arrange
        directory_path = './Test/'

        # Act
        files_in_directory(directory_path=directory_path, file_patterns=pattern)

        # Assert
        mock_function.assert_called_once_with(f'./Test/{pattern}', recursive=False)

    @parameterized.expand([
        [[], '.mp3'],
        [['a.mp3', 'b.mp3'], '.mp3'],
        [[], '*.txt'],
        [['a.txt', 'b.txt', 'c.txt'], '.*txt'],
        [[], '**.wav'],
        [['a.wav'], '.**wav'],
    ])
    @patch('glob.glob')
    def test_files_in_directory__OnePattern__ReturnsMockedData(
            self,
            data,
            pattern,
            mock_function: MagicMock,
    ):
        # Arrange
        directory_path = './Test/'
        length = len(data)
        mock_function.return_value = data

        # Act
        files = files_in_directory(directory_path=directory_path, file_patterns=pattern)

        # Assert
        self.assertIsInstance(files, List)
        self.assertEqual(len(files), length)
        self.assertListEqual(files, data)

    @parameterized.expand([[['.mp3']], [['.mp3', '*.txt']], [['.mp3', '*.txt', '**.wav']]])
    @patch('glob.glob')
    def test_files_in_directory__MultiPatterns__CallsGlobOncePerPattern(
            self,
            patterns,
            mock_function: MagicMock,
    ):
        # Arrange
        directory_path = './Test/'
        calls = [call(f'./Test/{pattern}', recursive=False) for pattern in patterns]

        # Act
        files_in_directory(directory_path=directory_path, file_patterns=patterns)

        # Assert
        mock_function.assert_has_calls(calls=calls, any_order=True)

    @unittest.skip
    @parameterized.expand([
        [[[]], ['.mp3'], []],
        [[['a.mp3', 'b.mp3']], ['.mp3'], ['a.mp3', 'b.mp3']],
        [[[], []], ['.mp3', '*.txt'], []],
        [[['a.mp3'], ['b.txt', 'c.txt']], ['.mp3', '.*txt'], ['a.mp3', 'b.txt', 'c.txt']],
        [[[], [], []], ['.mp3', '*.txt', '**.wav'], []],
        [[['a.mp3'], ['b.txt'], ['c.wav']], ['.mp3', '*.txt', '.**wav'], ['a.mp3', 'b.txt', 'c.wav']],
    ])
    @patch('glob.glob')
    def test_files_in_directory__MultiPattern__ReturnsMockedData(
            self,
            data,
            patterns,
            expected,
            mock_function: MagicMock,
    ):
        # Arrange
        directory_path = './Test/'
        mock_function.side_effect = data
        length = len(expected)

        # Act
        files = files_in_directory(directory_path=directory_path, file_patterns=patterns)

        # Assert
        self.assertIsInstance(files, List)
        self.assertEqual(len(files), length)
        self.assertListEqual(files, expected)
