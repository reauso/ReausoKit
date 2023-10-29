from __future__ import annotations

from ast import Bytes
from enum import unique, Enum
from math import ceil, floor

import numpy as np


@unique
class ByteChunkSize(Enum):
    BIT8 = 8
    BIT32 = 32
    BIT64 = 64

    @property
    def numpy_type(self):
        mapping = {
            self.BIT8: np.uint8,
            self.BIT32: np.uint32,
            self.BIT64: np.uint64,
        }
        return mapping[self]

    @property
    def value_range(self):
        mapping = {
            self.BIT8: 2 ** 8,
            self.BIT32: 2 ** 32,
            self.BIT64: 2 ** 64,
        }
        return mapping[self]


def array_to_bit_string(array, byte_size: ByteChunkSize, start_index: int | None = None, end_index: int | None = None,
                        with_space: bool = False):
    # init indices if not given
    start_index = 0 if start_index is None else start_index
    end_index = len(array) * byte_size.value if end_index is None else end_index

    # indices out of bounds validation
    if len(array) == 0:
        return ''
    if start_index >= len(array) * byte_size.value or start_index < -len(array) * byte_size.value:
        raise IndexError('array start index out of bounds!')
    if end_index > len(array) * byte_size.value or end_index < -len(array) * byte_size.value:
        raise IndexError('array end index out of bounds!')

    # indices to positive values
    start_index = len(array) * byte_size.value + start_index if start_index < 0 else start_index
    end_index = len(array) * byte_size.value + end_index if end_index < 0 else end_index

    # validate start < end index
    if start_index > end_index:
        raise ValueError(f'start index ({start_index}) > end index ({end_index}) is not allowed!')

    # to string
    bits = [bin(i)[2:] for i in array]
    bits = [''.join('0' for _ in range(byte_size.value - len(bit))) + bit for bit in bits]
    bits = ''.join(bits)
    bits = bits[start_index: end_index]

    if with_space:
        num_bits_left = len(bits)
        offset = 8 - (start_index % 8)
        spaced_bits = bits[:offset]
        num_bits_left -= offset

        while num_bits_left > 0:
            spaced_bits += ' '
            start = len(bits) - num_bits_left
            spaced_bits += bits[start: start + 8]
            num_bits_left -= 8
        bits = spaced_bits

    return bits


class BitArray:
    def __init__(self, size, byte_size: ByteChunkSize = ByteChunkSize.BIT64):
        self._size = size
        self._byte_size = byte_size

        np_dimensions = ceil(self._size / self._byte_size.value)
        self._array = np.zeros(np_dimensions, dtype=self._byte_size.numpy_type)

    def _set_bits(self, left_bit_index, value, num_bits):
        # TODO test (with array_to_bit_string method)

        right_bit_index = left_bit_index + num_bits - 1
        left_array_index = floor(left_bit_index / self._byte_size.value)
        right_array_index = floor(right_bit_index / self._byte_size.value)

        array_right_shifts = left_bit_index % self._byte_size.value
        array_left_shifts = (self._byte_size.value - (array_right_shifts + num_bits)) % self._byte_size.value
        value_right_shifts = num_bits - self._byte_size.value + array_right_shifts
        for i, package_index in enumerate(range(left_array_index, right_array_index + 1)):
            # calculate new value with shifting
            array_value = value >> value_right_shifts if value_right_shifts > 0 else value << abs(value_right_shifts)
            array_value = array_value % self._byte_size.value_range

            # calculate mask to reset only the values which are newly set
            mask = self._byte_size.value_range - 1
            if package_index == left_array_index == right_array_index:
                mask_left = mask >> self._byte_size.value - array_right_shifts
                mask_left = mask_left << self._byte_size.value - array_right_shifts
                mask_right = mask >> self._byte_size.value - array_left_shifts
                mask = mask_left | mask_right
            elif package_index == left_array_index:
                mask = mask >> self._byte_size.value - array_right_shifts
                mask = mask << self._byte_size.value - array_right_shifts
            elif package_index == right_array_index:
                mask = mask >> self._byte_size.value - array_left_shifts
            else:
                mask = 0

            # reset current value and then set new value
            self._array[package_index: package_index + 1] = \
                np.bitwise_and(self._array[package_index: package_index + 1], mask)
            self._array[package_index: package_index + 1] = \
                np.bitwise_or(self._array[package_index: package_index + 1], array_value)
            value_right_shifts -= self._byte_size.value

    def __getitem__(self, item) -> bool | Bytes:
        # TODO implement for single value and for slice. See:
        #  https://www.geeksforgeeks.org/implementing-slicing-in-__getitem__/

        if isinstance(item, int):
            # parameter validation
            if item < -self._size or item >= self._size:
                raise IndexError('array index out of range')

            # calculate necessary values
            item = item if item >= 0 else self._size + item
            array_index = floor(item / self._byte_size.value)
            left_shifts = self._byte_size.numpy_type(item % self._byte_size.value)
            right_shifts = self._byte_size.numpy_type(self._byte_size.value - 1)

            # determine bit value of boolean to return
            value = self._array[array_index]
            value = value << left_shifts
            value = value >> right_shifts

            return bool(value)

        elif isinstance(item, slice):
            # TODO return multiple bits
            #   Distinction between int input or array input
            print('slice')
            raise NotImplementedError('Not implemented yet!')

    def __setitem__(self, key, value):
        # TODO implement for single value and for slice. See:
        #  https://www.geeksforgeeks.org/implementing-slicing-in-__getitem__/
        raise NotImplementedError()

    def __str__(self):
        return self.as_string()

    def as_string(self, start_index: int = 0, end_index: int | None = None, with_space=False):
        end_index = self._size if end_index is None else end_index
        return array_to_bit_string(array=self._array, byte_size=self._byte_size,
                                   start_index=start_index, end_index=end_index, with_space=with_space)

    def as_formatted_string(self, start_index: int = 0, end_index: int | None = None, bytes_in_row: int = 10,
                            with_header=True):
        # check if parameter values are valid
        if bytes_in_row < 1:
            raise ValueError('The bytes_in_row minimum is 1. A value smaller than 1 is not allowed!')

        # if end index is None set the corresponding int value
        end_index = self._size if end_index is None else end_index

        # array to string
        bits = array_to_bit_string(array=self._array, byte_size=self._byte_size,
                                               start_index=start_index, end_index=end_index, with_space=False)

        # indices to positive values
        start_index = start_index if start_index >= 0 else self._size + start_index
        end_index = end_index if end_index >= 0 else self._size + end_index

        # necessary values to format bit string
        bits_to_show = end_index - start_index
        max_bits_per_row = bytes_in_row * 8
        padding_front = start_index % 8
        num_start_bits = (8 - padding_front) % 8
        num_total_bytes = ceil((end_index - start_index - num_start_bits) / 8)
        num_total_bytes += 1 if num_start_bits > 0 else 0
        first_byte_index = floor(start_index / 8)

        # container for formatted string
        formatted_bits = ''

        current_byte_index = first_byte_index
        current_bit_index = start_index

        num_rows = ceil(num_total_bytes / bytes_in_row) 
        for row in range(num_rows):
            bytes_in_current_row = min(num_total_bytes - (row * bytes_in_row), bytes_in_row)
            bits_in_current_row = min(bits_to_show, max_bits_per_row - padding_front) if row == 0 else \
                min(end_index - current_bit_index, max_bits_per_row)

            # add header
            if with_header:
                header_row = [i for i in range(current_byte_index, current_byte_index + bytes_in_current_row)]
                header_row = [str(i) + ''.join(' ' for _ in range(8 - len(str(i)))) for i in header_row]
                header_row = ' '.join(i for i in header_row) + '\n'

                formatted_bits += header_row

            # add formatted bits
            bit_row = ''.join(' ' for _ in range(padding_front)) if row == 0 else ''
            bit_row += bits[current_bit_index: current_bit_index + bits_in_current_row]
            bit_row = ' '.join(bit_row[i: i + 8] for i in range(0, len(bit_row), 8)) + '\n'
            formatted_bits += bit_row

            # update state
            current_byte_index += bytes_in_current_row
            current_bit_index += bits_in_current_row

        return formatted_bits[:-1]
