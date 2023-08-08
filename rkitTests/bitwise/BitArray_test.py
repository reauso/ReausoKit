import random
import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch

import numpy as np
from parameterized import parameterized

from rkit.bitwise.BitArray import ByteChunkSize, array_to_bit_string, BitArray
from rkitTests.bitwise.BitArray_test_data import ArrayToBitStringTestData, BitArrayTestData


class ArrayToBitStringTest(TestCase):
    data_provider = ArrayToBitStringTestData()

    @parameterized.expand(data_provider.array_to_bit_string__empty_array__returns_empty_string_data)
    def test_array_to_bit_string__empty_array__returns_empty_string(
            self,
            with_space,
            byte_size,
    ):
        # init
        array = []
        expected = ''

        # test
        actual = array_to_bit_string(array=array, byte_size=byte_size, with_space=with_space)

        # validate
        self.assertEqual(expected, actual)

    @parameterized.expand(
        data_provider.array_to_bit_string__without_space__returns_bit_string_without_spaces_data)
    def test_array_to_bit_string__without_space__returns_bit_string_without_spaces(
            self,
            data_id,
            array,
            expected,
            byte_size,
    ):
        # test
        actual = array_to_bit_string(array=array, byte_size=byte_size, with_space=False)

        # validate
        self.assertEqual(expected, actual, f'Actual value is not as expected for Parameters: data_id: {data_id} '
                                           f'array: {array}, byte_size: {byte_size}')

    @parameterized.expand(
        data_provider.array_to_bit_string__with_space__returns_bit_string_with_spaces_data)
    def test_array_to_bit_string__with_space__returns_bit_string_with_spaces(
            self,
            data_id,
            array,
            expected,
            byte_size,
    ):
        # test
        actual = array_to_bit_string(array=array, byte_size=byte_size, with_space=True)

        # validate
        self.assertEqual(expected, actual, f'Actual value is not as expected for Parameters: data_id: {data_id} '
                                           f'array: {array}, byte_size: {byte_size}')

    @parameterized.expand(
        data_provider.array_to_bit_string__without_space_and_indexed__returns_indexed_bit_string_without_spaces_data)
    def test_array_to_bit_string__without_space_and_indexed__returns_indexed_bit_string_without_spaces(
            self,
            data_id,
            array,
            expected,
            range,
            byte_size,
    ):
        # test
        actual = array_to_bit_string(array=array, start_index=range[0], end_index=range[1], byte_size=byte_size,
                                     with_space=False)

        # validate
        self.assertEqual(expected, actual, f'Actual value is not as expected for Parameters: data_id: {data_id} '
                                           f'array: {array}, range: {range}, byte_size: {byte_size}')

    @parameterized.expand(
        data_provider.array_to_bit_string__with_space_and_indexed__returns_indexed_bit_string_with_spaces_data)
    def test_array_to_bit_string__with_space_and_indexed__returns_indexed_bit_string_with_spaces(
            self,
            data_id,
            array,
            expected,
            index_range,
            byte_size,
    ):
        # test
        actual = array_to_bit_string(array=array, start_index=index_range[0], end_index=index_range[1],
                                     byte_size=byte_size,
                                     with_space=True)

        # validate
        self.assertEqual(expected, actual, f'Actual value is not as expected for Parameters: data_id: {data_id} '
                                           f'array: {array}, range: {index_range}, byte_size: {byte_size}')

    @parameterized.expand(data_provider.array_to_bit_string__start_index_out_of_bounds__raises_index_error_data)
    def test_array_to_bit_string__start_index_out_of_bounds__raises_index_error(
            self,
            data_id,
            array,
            byte_size,
    ):
        # init
        negative_bound = -len(array) * byte_size.value - 1
        positive_bound = len(array) * byte_size.value

        # test + validate
        with self.assertRaises(IndexError, msg=f'Negative Index Bound {negative_bound} does not raise IndexError: '
                                               f'data_id: {data_id} array: {array}, byte_size: {byte_size}'):
            array_to_bit_string(array=array, byte_size=byte_size, start_index=negative_bound)

        with self.assertRaises(IndexError, msg=f'Positive Index Bound {positive_bound} does not raise IndexError: '
                                               f'data_id: {data_id} array: {array}, byte_size: {byte_size}'):
            array_to_bit_string(array=array, byte_size=byte_size, start_index=positive_bound)

    @parameterized.expand(data_provider.array_to_bit_string__end_index_out_of_bounds__raises_index_error_data)
    def test_array_to_bit_string__end_index_out_of_bounds__raises_index_error(
            self,
            data_id,
            array,
            byte_size,
    ):
        # init
        negative_bound = -len(array) * byte_size.value - 1
        positive_bound = len(array) * byte_size.value + 1

        # test + validate
        with self.assertRaises(IndexError, msg=f'Negative Index Bound {negative_bound} does not raise IndexError: '
                                               f'data_id: {data_id} array: {array}, byte_size: {byte_size}'):
            array_to_bit_string(array=array, byte_size=byte_size, end_index=negative_bound)

        with self.assertRaises(IndexError, msg=f'Positive Index Bound {positive_bound} does not raise IndexError: '
                                               f'data_id: {data_id} array: {array}, byte_size: {byte_size}'):
            array_to_bit_string(array=array, byte_size=byte_size, end_index=positive_bound)

    @parameterized.expand(data_provider.array_to_bit_string__start_index_greater_end_index__raises_value_error_data)
    def test_array_to_bit_string__start_index_greater_end_index__raises_value_error(
            self,
            data_id,
            array,
            index_range,
            byte_size,
    ):
        # test + validate
        message = f'Expected to raise a Value Error: data_id: {data_id} array: {array}, ' \
                  f'start_index: {index_range[0]}, end_index: {index_range[1]}, ' \
                  f'byte_size: {byte_size}'

        with self.assertRaises(ValueError, msg=message):
            array_to_bit_string(array=array, byte_size=byte_size, start_index=index_range[0], end_index=index_range[1])


class BitArrayTest(TestCase):
    data_provider = BitArrayTestData()

    # TODO implement

    @parameterized.expand(data_provider.as_string__no_indices_no_space__returns_string_data)
    @patch('rkit.bitwise.BitArray.array_to_bit_string')
    def test_as_string__no_indices_no_space__returns_string(
            self,
            data_id,
            array_size,
            expected,
            byte_size: ByteChunkSize,
            mock_function: MagicMock,
    ):
        # init
        nparray = np.zeros(array_size, dtype=byte_size.numpy_type)
        mock_function.return_value = expected

        array = BitArray(array_size, byte_size=byte_size)
        array._array = nparray
        assert array._size == array_size
        assert array._byte_size == byte_size

        # test
        actual = array.as_string(with_space=False)

        # validate
        mock_function.assert_called_once_with(
            array=nparray,
            byte_size=byte_size,
            start_index=0,
            end_index=array_size,
            with_space=False,
        )
        message = (f"The actual value is different from the expected value with parameters: "
                   f"data id: {data_id}, array size: {array_size}, byte_size: {byte_size}"
                   f"\nexpected: {expected}"
                   f"\nactual  : {actual}")
        self.assertEqual(expected, actual, msg=message)

    @parameterized.expand(
        data_provider.as_string__no_indices_with_space__returns_string_with_byte_chunks_data)
    @patch('rkit.bitwise.BitArray.array_to_bit_string')
    def test_as_string__no_indices_with_space__returns_string_with_byte_chunks(
            self,
            data_id,
            array_size,
            expected,
            byte_size: ByteChunkSize,
            mock_function: MagicMock,
    ):
        # init
        nparray = np.zeros(array_size, dtype=byte_size.numpy_type)
        mock_function.return_value = expected

        array = BitArray(array_size, byte_size=byte_size)
        array._array = nparray
        assert array._size == array_size
        assert array._byte_size == byte_size

        # test
        actual = array.as_string(with_space=True)

        # validate
        mock_function.assert_called_once_with(
            array=nparray,
            byte_size=byte_size,
            start_index=0,
            end_index=array_size,
            with_space=True,
        )
        message = (f"The actual value is different from the expected value with parameters: "
                   f"data id: {data_id}, array size: {array_size}, byte_size: {byte_size}"
                   f"\nexpected: {expected}"
                   f"\nactual  : {actual}")
        self.assertEqual(expected, actual, msg=message)

    @parameterized.expand(
        data_provider.as_string__with_indices_no_space__returns_indexed_string_data)
    @patch('rkit.bitwise.BitArray.array_to_bit_string')
    def test_as_string__with_indices_no_space__returns_indexed_string(
            self,
            data_id,
            array_size,
            expected,
            indices,
            byte_size: ByteChunkSize,
            mock_function: MagicMock,
    ):
        # init
        nparray = np.zeros(array_size, dtype=byte_size.numpy_type)
        mock_function.return_value = expected

        array = BitArray(array_size, byte_size=byte_size)
        array._array = nparray
        assert array._size == array_size
        assert array._byte_size == byte_size

        # test
        actual = array.as_string(with_space=False, start_index=indices[0], end_index=indices[1])

        # validate
        mock_function.assert_called_once_with(
            array=nparray,
            byte_size=byte_size,
            start_index=indices[0],
            end_index=array_size if indices[1] is None else indices[1],
            with_space=False,
        )
        message = (f"The actual value is different from the expected value with parameters: "
                   f"data id: {data_id}, array size: {array_size}, byte_size: {byte_size}, indices: {indices}"
                   f"\nexpected: {expected}"
                   f"\nactual  : {actual}")
        self.assertEqual(expected, actual, msg=message)

    @parameterized.expand(
        data_provider.as_string__with_indices_with_space__returns_indexed_string_with_byte_chunks_data)
    @patch('rkit.bitwise.BitArray.array_to_bit_string')
    def test_as_string__with_indices_with_space__returns_indexed_string_with_byte_chunks(
            self,
            data_id,
            array_size,
            expected,
            indices,
            byte_size: ByteChunkSize,
            mock_function: MagicMock,
    ):
        # init
        nparray = np.zeros(array_size, dtype=byte_size.numpy_type)
        mock_function.return_value = expected

        array = BitArray(array_size, byte_size=byte_size)
        array._array = nparray
        assert array._size == array_size
        assert array._byte_size == byte_size

        # test
        actual = array.as_string(with_space=True, start_index=indices[0], end_index=indices[1])

        # validate
        mock_function.assert_called_once_with(
            array=nparray,
            byte_size=byte_size,
            start_index=indices[0],
            end_index=array_size if indices[1] is None else indices[1],
            with_space=True,
        )
        message = (f"The actual value is different from the expected value with parameters: "
                   f"data id: {data_id}, array size: {array_size}, byte_size: {byte_size}, indices: {indices}"
                   f"\nexpected: {expected}"
                   f"\nactual  : {actual}")
        self.assertEqual(expected, actual, msg=message)

    @parameterized.expand(data_provider.as_formatted_string__default_parameters__returns_expected_formatted_string_data)
    @patch('rkit.bitwise.BitArray.array_to_bit_string')
    def test_as_formatted_string__default_parameters__returns_expected_formatted_string(
            self,
            data_id,
            array_size,
            array_to_bit_string_return_value,
            formatted_string,
            byte_size,
            mock_function: MagicMock,
    ):
        # init
        nparray = np.zeros(array_size, dtype=byte_size.numpy_type)
        mock_function.return_value = array_to_bit_string_return_value

        array = BitArray(array_size, byte_size=byte_size)
        array._array = nparray
        assert array._size == array_size
        assert array._byte_size == byte_size

        # test
        actual = array.as_formatted_string()

        # validate
        mock_function.assert_called_once_with(
            array=nparray,
            byte_size=byte_size,
            start_index=0,
            end_index=array_size,
            with_space=False,
        )
        message = (f"The actual value is different from the expected value with parameters: "
                   f"data id: {data_id}, array size: {array_size}, byte_size: {byte_size}, "
                   f"array_to_bit_string_return_value: {array_to_bit_string_return_value}"
                   f"\nexpected: {formatted_string}"
                   f"\nactual  : {actual}")
        self.assertEqual(formatted_string, actual, msg=message)

    @parameterized.expand(data_provider.as_formatted_string__with_indices__returns_expected_formatted_string_data)
    @patch('rkit.bitwise.BitArray.array_to_bit_string')
    def test_as_formatted_string__with_indices__returns_expected_formatted_string(
            self,
            data_id,
            array_size,
            array_to_bit_string_return_value,
            indices,
            formatted_string,
            byte_size,
            mock_function: MagicMock,
    ):
        # init
        nparray = np.zeros(array_size, dtype=byte_size.numpy_type)
        mock_function.return_value = array_to_bit_string_return_value

        array = BitArray(array_size, byte_size=byte_size)
        array._array = nparray
        assert array._size == array_size
        assert array._byte_size == byte_size

        # test
        actual = array.as_formatted_string(start_index=indices[0], end_index=indices[1])

        # validate
        mock_function.assert_called_once_with(
            array=nparray,
            byte_size=byte_size,
            start_index=indices[0],
            end_index=array_size if indices[1] is None else indices[1],
            with_space=False,
        )
        message = (f"The actual value is different from the expected value with parameters: "
                   f"data id: {data_id}, array size: {array_size}, byte_size: {byte_size}, "
                   f"array_to_bit_string_return_value: {array_to_bit_string_return_value}, "
                   f"indices: {indices}"
                   f"\nexpected: {formatted_string}"
                   f"\nactual  : {actual}")
        self.assertEqual(formatted_string, actual, msg=message)

    @parameterized.expand(
        data_provider.as_formatted_string__changed_bytes_in_row__returns_expected_formatted_string_data)
    @patch('rkit.bitwise.BitArray.array_to_bit_string')
    def test_as_formatted_string__changed_bytes_in_row__returns_expected_formatted_string(
            self,
            data_id,
            array_size,
            array_to_bit_string_return_value,
            bytes_in_row,
            formatted_string,
            byte_size,
            mock_function: MagicMock,
    ):
        # init
        nparray = np.zeros(array_size, dtype=byte_size.numpy_type)
        mock_function.return_value = array_to_bit_string_return_value

        array = BitArray(array_size, byte_size=byte_size)
        array._array = nparray
        assert array._size == array_size
        assert array._byte_size == byte_size

        # test
        actual = array.as_formatted_string(bytes_in_row=bytes_in_row)

        # validate
        mock_function.assert_called_once_with(
            array=nparray,
            byte_size=byte_size,
            start_index=0,
            end_index=array_size,
            with_space=False,
        )
        message = (f"The actual value is different from the expected value with parameters: "
                   f"data id: {data_id}, array size: {array_size}, byte_size: {byte_size}, "
                   f"array_to_bit_string_return_value: {array_to_bit_string_return_value}, "
                   f"bytes_in_row: {bytes_in_row}"
                   f"\nexpected: {formatted_string}"
                   f"\nactual  : {actual}")
        self.assertEqual(formatted_string, actual, msg=message)

    @parameterized.expand(data_provider.as_formatted_string__invalid_bytes_in_row__raises_value_error_data)
    @patch('rkit.bitwise.BitArray.array_to_bit_string')
    def test_as_formatted_string__invalid_bytes_in_row__raises_value_error(
            self,
            data_id,
            array_size,
            array_to_bit_string_return_value,
            invalid_bytes_in_row,
            byte_size,
            mock_function: MagicMock,
    ):
        # init
        nparray = np.zeros(array_size, dtype=byte_size.numpy_type)
        mock_function.return_value = array_to_bit_string_return_value

        array = BitArray(array_size, byte_size=byte_size)
        array._array = nparray
        assert array._size == array_size
        assert array._byte_size == byte_size

        # test + validate
        message = 'The bytes_in_row minimum is 1. A value smaller than 1 is not allowed!'

        with self.assertRaises(ValueError, msg=message):
            actual = array.as_formatted_string(bytes_in_row=invalid_bytes_in_row)

        # validate
        mock_function.assert_not_called()

    @parameterized.expand(data_provider.as_formatted_string__without_header__returns_expected_formatted_string_data)
    @patch('rkit.bitwise.BitArray.array_to_bit_string')
    def test_as_formatted_string__without_header__returns_expected_formatted_string(
            self,
            data_id,
            array_size,
            array_to_bit_string_return_value,
            formatted_string,
            byte_size,
            mock_function: MagicMock,
    ):
        # init
        nparray = np.zeros(array_size, dtype=byte_size.numpy_type)
        mock_function.return_value = array_to_bit_string_return_value

        array = BitArray(array_size, byte_size=byte_size)
        array._array = nparray
        assert array._size == array_size
        assert array._byte_size == byte_size

        # test
        actual = array.as_formatted_string(with_header=False)

        # validate
        mock_function.assert_called_once_with(
            array=nparray,
            byte_size=byte_size,
            start_index=0,
            end_index=array_size,
            with_space=False,
        )
        message = (f"The actual value is different from the expected value with parameters: "
                   f"data id: {data_id}, array size: {array_size}, byte_size: {byte_size}, "
                   f"array_to_bit_string_return_value: {array_to_bit_string_return_value}"
                   f"\nexpected: {formatted_string}"
                   f"\nactual  : {actual}")
        self.assertEqual(formatted_string, actual, msg=message)

    # TODO remove
    @unittest.skip
    def test_temp(self):
        print('----------------TEMP------------------')
        print(str(np.random.randint(2, size=779))[1: -1].replace(' ', '').replace('\n', ''))

        # pairwise
        a = [1, 2]
        b = [3, 4]
        c = {'a': 20, 'b': 30}
        # print(list(itertools.product([('h', 'j')], c.items())))
        # print(list(zip(a, b, c)))

        max_value = 779
        pairs = [(random.randrange(-max_value + 1, max_value), random.randrange(-max_value + 1, max_value)) for _ in
                 range(20)]
        pairs = [(min(a, b), max(a, b)) for (a, b) in pairs]
        print(pairs)

        self.assertTrue(False)
