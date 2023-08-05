import itertools
import random
import unittest
from math import floor
from unittest import TestCase
from unittest.mock import MagicMock, patch

import numpy as np
from parameterized import parameterized

from util.BitArray import ByteChunkSize, array_to_bit_string, BitArray


class ArrayToBitStringTest(TestCase):
    # TODO rework parameters like in BitArrayTest (e.g. names)
    # Data consists of :
    #   - id
    #   - python int array (hexadecimal)
    #   - Bit String without Spaces
    #   - Bit String with Spaces
    #   - Intervals to test / Index Boundaries to test
    #   - Byte Chunk Size
    data = [
        (
            0,
            [0x01, 0x10, 0x00, 0xDA, 0x4F, 0xFF, 0x00, 0x45],
            '0000000100010000000000001101101001001111111111110000000001000101',
            '00000001 00010000 00000000 11011010 01001111 11111111 00000000 01000101',
            [(0, 0), (1, 62), (1, None), (24, 43), (13, 54), (-43, -34), (-64, -1), (0, 63)],  # TODO test for None
            ByteChunkSize.BIT8,
        ),
        (
            1,
            [0x011000DA, 0x4FFF0000, 0x26FFA9EB, 0x002D0067],
            '0000000100010000000000001101101001001111111111110000000000000000001001101111111110101001111010110000000000'
            '1011010000000001100111',
            '00000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 10101001 '
            '11101011 00000000 00101101 00000000 01100111',
            [(0, 0), (1, 126), (1, None), (24, 86), (13, 77), (-96, -23), (-128, -1), (0, 127)],  # TODO test for None
            ByteChunkSize.BIT32,
        ),
        (
            2,
            [0x011000DA4FFF0000, 0x26FFA9EBF0F6AEB8, 0x7DC2059ABE29B290, 0x002D0067EF2051ED],
            '0000000100010000000000001101101001001111111111110000000000000000001001101111111110101001111010111111000011'
            '1101101010111010111000011111011100001000000101100110101011111000101001101100101001000000000000001011010000'
            '00000110011111101111001000000101000111101101',
            '00000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 10101001 '
            '11101011 11110000 11110110 10101110 10111000 01111101 11000010 00000101 10011010 10111110 00101001 '
            '10110010 10010000 00000000 00101101 00000000 01100111 11101111 00100000 01010001 11101101',
            [(0, 0), (1, 254), (1, None), (24, 234), (13, 177), (-30, -12), (-256, -1), (0, 255)],  # TODO test for None
            ByteChunkSize.BIT64,
        ),
    ]

    @parameterized.expand(
        list(itertools.product([True, False], list(ByteChunkSize)))
    )
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

    # [(id, array, Bit String without Spaces, ByteChunkSize), ...]
    without_test_params = [(a, b, c, d) for (a, b, c, _, _, d) in data]

    @parameterized.expand(without_test_params)
    def test_array_to_bit_string__without_space__returns_bit_string_representation_without_spaces(
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

    # [(id, array, Bit String with Spaces, ByteChunkSize), ...]
    with_test_params = [(a, b, c, d) for (a, b, _, c, _, d) in data]

    @parameterized.expand(with_test_params)
    def test_array_to_bit_string__with_space__returns_bit_string_representation_with_spaces(
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

    # [(id, array, Bit String without Spaces, One Index Boundary Tuple, ByteChunkSize), ...]
    without_indexed_test_params = [(a, b, c, d, e) for (a, b, c, _, d, e) in data]
    without_indexed_test_params = [itertools.product([(a, b, c, e)], d) for (a, b, c, d, e) in
                                   without_indexed_test_params]
    without_indexed_test_params = [(a, b, c, e, d) for product in without_indexed_test_params for ((a, b, c, d), e) in
                                   list(product)]

    @parameterized.expand(without_indexed_test_params)
    def test_array_to_bit_string__without_space_and_indexed__returns_indexed_bit_string_representation_without_spaces(
            self,
            data_id,
            array,
            expected,
            range,
            byte_size,
    ):
        # init
        expected = expected[range[0]: range[1]]

        # test
        actual = array_to_bit_string(array=array, start_index=range[0], end_index=range[1], byte_size=byte_size,
                                     with_space=False)

        # validate
        self.assertEqual(expected, actual, f'Actual value is not as expected for Parameters: data_id: {data_id} '
                                           f'array: {array}, range: {range}, byte_size: {byte_size}')

    # [(id, array, Bit String with Spaces, One Index Boundary Tuple, ByteChunkSize), ...]
    with_indexed_test_params = [(a, b, c, d, e) for (a, b, _, c, d, e) in data]
    with_indexed_test_params = [itertools.product([(a, b, c, e)], d) for (a, b, c, d, e) in
                                with_indexed_test_params]
    with_indexed_test_params = [(a, b, c, e, d) for product in with_indexed_test_params for ((a, b, c, d), e) in
                                list(product)]

    @parameterized.expand(with_indexed_test_params)
    def test_array_to_bit_string__with_space_and_indexed__returns_indexed_bit_string_representation_with_spaces(
            self,
            data_id,
            array,
            expected,
            index_range,
            byte_size,
    ):
        # TODO add custom params for this test and remove logic from this test!
        # init
        start_index = len(array) * byte_size.value + index_range[0] if index_range[0] < 0 else index_range[0]
        end_index = len(array) * byte_size.value + index_range[1] if index_range[1] < 0 else index_range[1]
        spaces_before_expected = floor(start_index / 8)
        spaces_in_expected = floor(end_index / 8) - spaces_before_expected
        expected = expected[
                   start_index + spaces_before_expected: end_index + spaces_before_expected + spaces_in_expected]

        # test
        actual = array_to_bit_string(array=array, start_index=index_range[0], end_index=index_range[1],
                                     byte_size=byte_size,
                                     with_space=True)

        # validate
        self.assertEqual(expected, actual, f'Actual value is not as expected for Parameters: data_id: {data_id} '
                                           f'array: {array}, range: {index_range}, byte_size: {byte_size}')

    # [(id, array, ByteChunkSize), ...]
    out_bounds_test_params = [(a, b, c) for (a, b, _, _, _, c) in data]

    @parameterized.expand(out_bounds_test_params)
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

    @parameterized.expand(out_bounds_test_params)
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

    # [(id, array, One Index Boundary Tuple, ByteChunkSize), ...]
    start_greater_end_test_params = [(a, b, c, d) for (a, b, _, _, c, d) in data]
    start_greater_end_test_params = [itertools.product([(a, b, d)], c) for (a, b, c, d) in
                                     start_greater_end_test_params]
    start_greater_end_test_params = [(a, b, d, c) for product in start_greater_end_test_params for ((a, b, c), d) in
                                     list(product)]

    @parameterized.expand(start_greater_end_test_params)
    def test_array_to_bit_string__start_index_greater_end_index__raises_value_error(
            self,
            data_id,
            array,
            index_range,
            byte_size,
    ):
        # TODO add custom indices for this test
        # If indices are the same add 1 to start index
        if index_range[0] == index_range[1]:
            index_range = (index_range[0], index_range[1] + 1)

        # test + validate
        message = f'Expected to raise a Value Error: data_id: {data_id} array: {array}, ' \
                  f'start_index: {index_range[1]}, end_index: {index_range[0]}, ' \
                  f'byte_size: {byte_size}'

        with self.assertRaises(ValueError, msg=message):
            array_to_bit_string(array=array, byte_size=byte_size, start_index=index_range[1], end_index=index_range[0])


class BitArrayTest(TestCase):
    # TODO implement

    byte_sizes = list(ByteChunkSize)
    as_string_data = [
        (
            # array_length
            200,
            # expected string without spaces
            '100000001011110011110101010001101010000001101100110010111001111011011000001101111111000101100101011000'
            '11000101000111111001011010010110111111111111010100011011011001110101001101111110101111000000011001',
            # expected string with spaces
            '10000000 10111100 11110101 01000110 10100000 01101100 11001011 10011110 11011000 00110111 11110001 '
            '01100101 01100011 00010100 01111110 01011010 01011011 11111111 11010100 01101101 10011101 01001101 '
            '11111010 11110000 00011001',
            # indices
            [(0, 0), (1, 195), (52, 86), (13, 123), (-12, -63), (-138, -1), (2, 53), (0, 199), (5, None)],
        ),
        (
            # array_length
            400,
            # expected string without spaces
            '1101001010101001001110001101011100011100100000011001011011000101110000010000110110000001011010111001101'
            '1100110101010111011100000110101100100010011011101011101010100110011101011111100101011111010010110101111'
            '0011000100011101010001010101001010010010111000101011011001001110110011111111000000101111010010001001100'
            '0101001010110010101101111110111100111011111101010101010110011100100001100111000011010010110',
            # expected string with spaces
            '11010010 10101001 00111000 11010111 00011100 10000001 10010110 11000101 11000001 00001101 10000001 '
            '01101011 10011011 10011010 10101110 11100000 11010110 01000100 11011101 01110101 01001100 11101011 '
            '11110010 10111110 10010110 10111100 11000100 01110101 00010101 01001010 01001011 10001010 11011001 '
            '00111011 00111111 11000000 10111101 00100010 01100010 10010101 10010101 10111111 01111001 11011111 '
            '10101010 10101100 11100100 00110011 10000110 10010110',
            # indices
            [(0, 0), (1, 195), (141, -171), (95, 282), (73, 110), (-283, 275), (-177, 351), (345, 399), (5, None)],
        ),
        (
            # array_length
            800,
            # expected string without spaces
            '10111001000011110110010011010110000000000011101011011101010110010100110000110011011100001111101010100010'
            '10001100010110100111101000110101110011110111011010010001101011110001000100001101111010001000001100110111'
            '11010011001110010111101111100100010110100110110100101000010010101111011110000001111110101101000101111111'
            '01101111101101111100111011100111100011111011100101011000100110011000010110011101100011110110100001010001'
            '01000111110011001101110111010111011111110010001101101001100000001010111111110110001010110110001010010000'
            '10011111000100111111010100100010111000010100001101110111111100111010001111110010101111111110100110011000'
            '00110111100111100110001001001100010010000111111101011100011101011001001011011000110010011111110101101110'
            '100100011010100011100111101100101100000100110111101101010000110101110010',
            # expected string with spaces
            '10111001 00001111 01100100 11010110 00000000 00111010 11011101 01011001 01001100 00110011 01110000 '
            '11111010 10100010 10001100 01011010 01111010 00110101 11001111 01110110 10010001 10101111 00010001 '
            '00001101 11101000 10000011 00110111 11010011 00111001 01111011 11100100 01011010 01101101 00101000 '
            '01001010 11110111 10000001 11111010 11010001 01111111 01101111 10110111 11001110 11100111 10001111 '
            '10111001 01011000 10011001 10000101 10011101 10001111 01101000 01010001 01000111 11001100 11011101 '
            '11010111 01111111 00100011 01101001 10000000 10101111 11110110 00101011 01100010 10010000 10011111 '
            '00010011 11110101 00100010 11100001 01000011 01110111 11110011 10100011 11110010 10111111 11101001 '
            '10011000 00110111 10011110 01100010 01001100 01001000 01111111 01011100 01110101 10010010 11011000 '
            '11001001 11111101 01101110 10010001 10101000 11100111 10110010 11000001 00110111 10110101 00001101 '
            '01110010',
            # indices
            [(0, 0), (1, 195), (-448, 567), (-614, -361), (30, 779), (-371, 659), (-492, -144), (-384, 799), (5, None)],
        ),
    ]

    # [(array_length, expected string without spaces, ByteChunkSize), ...]
    parameters = itertools.product(as_string_data, byte_sizes)
    parameters = [(a, b, c) for ((a, b, _, _), c) in list(parameters)]

    @parameterized.expand(parameters)
    @patch('util.BitArray.array_to_bit_string')
    def test_as_string__no_indices_no_space__returns_string_representation(
            self,
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
        self.assertEqual(expected, actual)

    # [(array_length, expected string with spaces, ByteChunkSize), ...]
    parameters = itertools.product(as_string_data, byte_sizes)
    parameters = [(a, b, c) for ((a, _, b, _), c) in list(parameters)]

    @parameterized.expand(parameters)
    @patch('util.BitArray.array_to_bit_string')
    def test_as_string__no_indices_with_space__returns_string_representation_with_byte_chunks(
            self,
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
        self.assertEqual(expected, actual)

    # [(array_size, expected string without spaces, One indices pair, ByteChunkSize), ...]
    parameters = [list(itertools.product([(a, b)], c)) for a, b, _, c in as_string_data]
    parameters = [(a, b, c) for product in parameters for ((a, b), c) in product]
    parameters = itertools.product(parameters, byte_sizes)
    parameters = [(a, b, c, d) for ((a, b, c), d) in list(parameters)]

    @parameterized.expand(parameters)
    @patch('util.BitArray.array_to_bit_string')
    def test_as_string__with_indices_no_space__returns_indexed_string_representation(
            self,
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
        self.assertEqual(expected, actual)

    # [(array_size, expected string with spaces, One indices pair, ByteChunkSize), ...]
    parameters = [list(itertools.product([(a, b)], c)) for a, _, b, c in as_string_data]
    parameters = [(a, b, c) for product in parameters for ((a, b), c) in product]
    parameters = itertools.product(parameters, byte_sizes)
    parameters = [(a, b, c, d) for ((a, b, c), d) in list(parameters)]

    @parameterized.expand(parameters)
    @patch('util.BitArray.array_to_bit_string')
    def test_as_string__with_indices_with_space__returns_indexed_string_representation_with_byte_chunks(
            self,
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
        self.assertEqual(expected, actual)

    # TODO add more
    as_formatted_string_data = [
        (
            # array_size
            200,
            # return of array_to_bit_string mock
            '10001011001111100110110110111011000100111011011110111101100101010011111111110001011000101010000000101111'
            '000101101001100001010001000001110110110000110110100011100111101111111111000100110100101110110110',
            # expected formatted string
            '0        1        2        3        4        5        6        7        8        9       \n'
            '10001011 00111110 01101101 10111011 00010011 10110111 10111101 10010101 00111111 11110001\n'
            '10       11       12       13       14       15       16       17       18       19      \n'
            '01100010 10100000 00101111 00010110 10011000 01010001 00000111 01101100 00110110 10001110\n'
            '20       21       22       23       24      \n'
            '01111011 11111111 00010011 01001011 10110110',
            # expected formatted string without header
            '10001011 00111110 01101101 10111011 00010011 10110111 10111101 10010101 00111111 11110001\n'
            '01100010 10100000 00101111 00010110 10011000 01010001 00000111 01101100 00110110 10001110\n'
            '01111011 11111111 00010011 01001011 10110110',
            # paris of indices and expected formatted Strings
            {
                (0, 0):
                    '',
                (12, 125):
                    '1        2        3        4        5        6        7        8        9        10      \n'
                    '    1110 01101101 10111011 00010011 10110111 10111101 10010101 00111111 11110001 01100010\n'
                    '11       12       13       14       15      \n'
                    '10100000 00101111 00010110 10011000 01010',
                (-83, 199):
                    '14       15       16       17       18       19       20       21       22       23      \n'
                    '     000 01010001 00000111 01101100 00110110 10001110 01111011 11111111 00010011 01001011\n'
                    '24      \n'
                    '1011011',
                (-93, -92):
                    '13      \n'
                    '   1',
            },
            # pairs of bytes in row and expected formatted Strings
            {
                2:
                    '',
                8:
                    '',
                15:
                    '',
                20:
                    '',
            },
        ),
    ]

    # [(array_size, array_to_bit_string return, expected string, ByteChunkSize), ...]
    parameters = itertools.product(as_formatted_string_data, byte_sizes)
    parameters = [(a, b, c, d) for ((a, b, c, _, _, _), d) in list(parameters)]

    @parameterized.expand(parameters)
    @patch('util.BitArray.array_to_bit_string')
    def test_as_formatted_string__default_parameters__returns_expected_formatted_string_representation(
            self,
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
        self.assertEqual(formatted_string, actual)

    # [(array_size, array_to_bit_string return, indices, expected string, ByteChunkSize), ...]
    parameters = [list(itertools.product([(a, b)], c.items())) for a, b, _, _, c, _ in as_formatted_string_data]
    parameters = [(a, b, c, d) for product in parameters for ((a, b), (c, d)) in product]
    parameters = itertools.product(parameters, byte_sizes)
    parameters = [(a, b, c, d, e) for ((a, b, c, d), e) in list(parameters)]

    @parameterized.expand(parameters)
    @patch('util.BitArray.array_to_bit_string')
    def test_as_formatted_string__with_indices__returns_expected_formatted_string_representation(
            self,
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
        self.assertEqual(formatted_string, actual)

    # @unittest.skip("NotImplemented")
    # def test_as_formatted_string__changed_bytes_in_row__returns_expected_formatted_string_representation(self):
    #     # TODO implement + mock array_to_bit_string
    #     raise NotImplementedError()

    # [(array_size, array_to_bit_string return, invalid bytes_in_row, ByteChunkSize), ...]
    invalid_bytes_in_row = [0, -2, -32, -18]
    parameters = itertools.product(as_formatted_string_data, invalid_bytes_in_row, byte_sizes)
    parameters = [(a, b, c, d) for ((a, b, _, _, _, _), c, d) in list(parameters)]

    @parameterized.expand(parameters)
    @patch('util.BitArray.array_to_bit_string')
    def test_as_formatted_string__invalid_bytes_in_row__raises_value_error(
            self,
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

    # [(array_size, array_to_bit_string return, expected string without header, ByteChunkSize), ...]
    parameters = itertools.product(as_formatted_string_data, byte_sizes)
    parameters = [(a, b, c, d) for ((a, b, _, c, _, _), d) in list(parameters)]

    @parameterized.expand(parameters)
    @patch('util.BitArray.array_to_bit_string')
    def test_as_formatted_string__without_header__returns_expected_formatted_string_representation(
            self,
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
        self.assertEqual(formatted_string, actual)

    # TODO remove
    def test_temp(self):
        print('----------------TEMP------------------')
        print(str(np.random.randint(2, size=400))[1: -1].replace(' ', '').replace('\n', ''))

        # pairwise
        a = [1, 2]
        b = [3, 4]
        c = {'a': 20, 'b': 30}
        # print(list(itertools.product([('h', 'j')], c.items())))
        # print(list(zip(a, b, c)))

        max_value = 200
        pairs = [(random.randrange(-max_value + 1, max_value), random.randrange(-max_value + 1, max_value)) for _ in
                 range(20)]
        pairs = [(min(a, b), max(a, b)) for (a, b) in pairs]
        print(pairs)

        # print(8 % 8)

        self.assertTrue(False)
