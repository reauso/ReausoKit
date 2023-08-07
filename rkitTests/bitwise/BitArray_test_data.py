import itertools

from rkit.bitwise.BitArray import ByteChunkSize


class ArrayToBitStringTestData:
    def __init__(self):
        self._data = None
        """
        List of dicts with:
        
        - id: int
        - array: list[int]
        - string: str
        - string_spaced: str
        - intervals: {(int, int): str (expected with spaces), ...}
        - reversed_intervals: [(int, int), ...]
        - chunk_size: ByteChunkSize
        """

        self.__define_data()

    def __define_data(self):
        self._data = [
            {
                'id':
                    0,
                'array':
                    [0x01, 0x10, 0x00, 0xDA, 0x4F, 0xFF, 0x00, 0x45],
                'string':
                    '0000000100010000000000001101101001001111111111110000000001000101',
                'string_spaced':
                    '00000001 00010000 00000000 11011010 01001111 11111111 00000000 01000101',
                'intervals':
                    {
                        (0, 0):
                            '',
                        (1, 62):
                            '0000001 00010000 00000000 11011010 01001111 11111111 00000000 010001',
                        (1, None):
                            '0000001 00010000 00000000 11011010 01001111 11111111 00000000 01000101',
                        (None, 16):
                            '00000001 00010000',
                        (24, 43):
                            '11011010 01001111 111',
                        (13, 54):
                            '000 00000000 11011010 01001111 11111111 000000',
                        (-43, -34):
                            '000 110110',
                        (-64, -1):
                            '00000001 00010000 00000000 11011010 01001111 11111111 00000000 0100010',
                        (0, 63):
                            '00000001 00010000 00000000 11011010 01001111 11111111 00000000 0100010'
                    },
                'reversed_intervals':
                    [(20, 10), (63, 12), (34, -40), (-20, 20), (-13, -44), (54, 12), (-18, -19), (2, 1)],
                'chunk_size':
                    ByteChunkSize.BIT8,
            },
            {
                'id':
                    1,
                'array':
                    [0x011000DA, 0x4FFF0000, 0x26FFA9EB, 0x002D0067],
                'string':
                    '000000010001000000000000110110100100111111111111000000000000000000100110111111111010100111101'
                    '01100000000001011010000000001100111',
                'string_spaced':
                    '00000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 '
                    '10101001 11101011 00000000 00101101 00000000 01100111',
                'intervals':
                    {
                        (0, 0):
                            '',
                        (1, 126):
                            '0000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 '
                            '10101001 11101011 00000000 00101101 00000000 011001',
                        (1, None):
                            '0000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 '
                            '10101001 11101011 00000000 00101101 00000000 01100111',
                        (None, 16):
                            '00000001 00010000',
                        (24, 86):
                            '11011010 01001111 11111111 00000000 00000000 00100110 11111111 101010',
                        (13, 77):
                            '000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111',
                        (-96, -23):
                            '01001111 11111111 00000000 00000000 00100110 11111111 10101001 11101011 00000000 0',
                        (-128, -1):
                            '00000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 '
                            '10101001 11101011 00000000 00101101 00000000 0110011',
                        (0, 127):
                            '00000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 '
                            '10101001 11101011 00000000 00101101 00000000 0110011'
                    },
                'reversed_intervals':
                    [(50, 20), (127, 43), (34, -120), (-20, 63), (-26, -83), (54, 12), (-18, -19), (2, 1)],
                'chunk_size':
                    ByteChunkSize.BIT32,
            },
            {
                'id':
                    2,
                'array':
                    [0x011000DA4FFF0000, 0x26FFA9EBF0F6AEB8, 0x7DC2059ABE29B290, 0x002D0067EF2051ED],
                'string':
                    '00000001000100000000000011011010010011111111111100000000000000000010011011111111101010011110101'
                    '11111000011110110101011101011100001111101110000100000010110011010101111100010100110110010100100'
                    '000000000000101101000000000110011111101111001000000101000111101101',
                'string_spaced':
                    '00000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 '
                    '10101001 11101011 11110000 11110110 10101110 10111000 01111101 11000010 00000101 10011010 '
                    '10111110 00101001 10110010 10010000 00000000 00101101 00000000 01100111 11101111 00100000 '
                    '01010001 11101101',
                'intervals':
                    {
                        (0, 0):
                            '',
                        (1, 254):
                            '0000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 '
                            '10101001 11101011 11110000 11110110 10101110 10111000 01111101 11000010 00000101 10011010 '
                            '10111110 00101001 10110010 10010000 00000000 00101101 00000000 01100111 11101111 00100000 '
                            '01010001 111011',
                        (1, None):
                            '0000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 '
                            '10101001 11101011 11110000 11110110 10101110 10111000 01111101 11000010 00000101 10011010 '
                            '10111110 00101001 10110010 10010000 00000000 00101101 00000000 01100111 11101111 00100000 '
                            '01010001 11101101',
                        (None, 16):
                            '00000001 00010000',
                        (24, 234):
                            '11011010 01001111 11111111 00000000 00000000 00100110 11111111 10101001 11101011 11110000 '
                            '11110110 10101110 10111000 01111101 11000010 00000101 10011010 10111110 00101001 10110010 '
                            '10010000 00000000 00101101 00000000 01100111 11101111 00',
                        (13, 177):
                            '000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 10101001 '
                            '11101011 11110000 11110110 10101110 10111000 01111101 11000010 00000101 10011010 10111110 '
                            '00101001 1',
                        (-30, -12):
                            '101111 00100000 0101',
                        (-256, -1):
                            '00000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 '
                            '10101001 11101011 11110000 11110110 10101110 10111000 01111101 11000010 00000101 10011010 '
                            '10111110 00101001 10110010 10010000 00000000 00101101 00000000 01100111 11101111 00100000 '
                            '01010001 1110110',
                        (0, 255):
                            '00000001 00010000 00000000 11011010 01001111 11111111 00000000 00000000 00100110 11111111 '
                            '10101001 11101011 11110000 11110110 10101110 10111000 01111101 11000010 00000101 10011010 '
                            '10111110 00101001 10110010 10010000 00000000 00101101 00000000 01100111 11101111 00100000 '
                            '01010001 1110110',
                    },
                'reversed_intervals':
                    [(170, 30), (199, 43), (34, -240), (-20, 174), (-63, -128), (154, 26), (-18, -19), (2, 1)],
                'chunk_size':
                    ByteChunkSize.BIT64,
            },
        ]

    @property
    def array_to_bit_string__empty_array__returns_empty_string_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(with_space, Byte Chunk Size), ...]
        """
        parameters = list(itertools.product([True, False], list(ByteChunkSize)))
        return parameters

    @property
    def array_to_bit_string__without_space__returns_bit_string_without_spaces_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, hexadecimal array, Bit String without Spaces, ByteChunkSize), ...]
        """
        parameters = [(entry['id'], entry['array'], entry['string'], entry['chunk_size']) for entry in self._data]
        return parameters

    @property
    def array_to_bit_string__with_space__returns_bit_string_with_spaces_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, hexadecimal array, Bit String with Spaces, ByteChunkSize), ...]
        """
        parameters = [(entry['id'], entry['array'], entry['string_spaced'], entry['chunk_size']) for entry in
                      self._data]
        return parameters

    @property
    def array_to_bit_string__without_space_and_indexed__returns_indexed_bit_string_without_spaces_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, hexadecimal array, Bit String without Spaces, One Index Boundary Tuple, ByteChunkSize), ...]
        """
        parameters = [
            itertools.product(
                [(entry['id'], entry['array'], entry['string'], entry['chunk_size'])],
                list(entry['intervals'].items()),
            ) for entry in self._data]
        parameters = [(a, b, c, d, e[0]) for product in parameters for ((a, b, c, d), e) in list(product)]
        parameters = [(a, b, c[e[0]: e[1]], e, d) for (a, b, c, d, e) in parameters]

        return parameters

    @property
    def array_to_bit_string__with_space_and_indexed__returns_indexed_bit_string_with_spaces_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array, Bit String with Spaces, One Index Boundary Tuple, ByteChunkSize), ...]
        """
        parameters = [
            itertools.product(
                [(entry['id'], entry['array'], entry['chunk_size'])],
                list(entry['intervals'].items()),
            ) for entry in self._data]
        parameters = [(a, b, d[1], d[0], c) for product in parameters for ((a, b, c), d) in list(product)]

        return parameters

    @property
    def array_to_bit_string__start_index_out_of_bounds__raises_index_error_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array, ByteChunkSize), ...]
        """
        parameters = [(entry['id'], entry['array'], entry['chunk_size']) for entry in self._data]

        return parameters

    @property
    def array_to_bit_string__end_index_out_of_bounds__raises_index_error_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array, ByteChunkSize), ...]
        """
        parameters = [(entry['id'], entry['array'], entry['chunk_size']) for entry in self._data]

        return parameters

    @property
    def array_to_bit_string__start_index_greater_end_index__raises_value_error_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array, One Index Boundary Tuple, ByteChunkSize), ...]
        """
        parameters = [
            itertools.product(
                [(entry['id'], entry['array'], entry['chunk_size'])],
                entry['reversed_intervals'],
            ) for entry in self._data]
        parameters = [(a, b, d, c) for product in parameters for ((a, b, c), d) in list(product)]

        return parameters


class BitArrayTestData:
    def __init__(self):
        self._byte_chunk_sizes = list(ByteChunkSize)
        """
        Contains all existing ByteChunkSize values in a list.
        """
        self._as_string_data = None
        """
        List of dicts with:
        
        - id: int
        - array_size: int
        - array: list[int]
        - string: str
        - string_spaced: str
        - intervals: [(int, int), ...]
        """
        self.as_formatted_string_data = None
        """
        List of dicts with:
        
        - id: int
        - array_size: int
        - mock_return: str
        - string_headed: str
        - string: str
        - intervals: {(int, int): str (formatted headed str), ...}
        - bytes_in_row: {int: str (formatted headed str), ...}
        """
        self._as_formatted_string_invalid_bytes_in_row = [0, -2, -32, -18]
        """
        Invalid bytes_in_row parameter values for as_formatted_string method.
        """

        self.__define_as_string_data()
        self.__define_as_formatted_string_data()

    def __define_as_string_data(self):
        self._as_string_data = [
            {
                'id':
                    0,
                'array_size':
                    200,
                'string':
                    '10000000101111001111010101000110101000000110110011001011100111101101100000110111111100010110010101'
                    '10001100010100011111100101101001011011111111111101010001101101100111010100110111111010111100000001'
                    '1001',
                'string_spaced':
                    '10000000 10111100 11110101 01000110 10100000 01101100 11001011 10011110 11011000 00110111 '
                    '11110001 01100101 01100011 00010100 01111110 01011010 01011011 11111111 11010100 01101101 '
                    '10011101 01001101 11111010 11110000 00011001',
                'intervals':
                    [(0, 0), (1, 195), (52, 86), (13, 123), (-12, -63), (-138, -1), (2, 53), (0, 199), (5, None)],
            },
            {
                'id':
                    1,
                'array_size':
                    400,
                'string':
                    '11010010101010010011100011010111000111001000000110010110110001011100000100001101100000010110101110'
                    '01101110011010101011101110000011010110010001001101110101110101010011001110101111110010101111101001'
                    '01101011110011000100011101010001010101001010010010111000101011011001001110110011111111000000101111'
                    '01001000100110001010010101100101011011111101111001110111111010101010101100111001000011001110000110'
                    '10010110',
                'string_spaced':
                    '11010010 10101001 00111000 11010111 00011100 10000001 10010110 11000101 11000001 00001101 '
                    '10000001 01101011 10011011 10011010 10101110 11100000 11010110 01000100 11011101 01110101 '
                    '01001100 11101011 11110010 10111110 10010110 10111100 11000100 01110101 00010101 01001010 '
                    '01001011 10001010 11011001 00111011 00111111 11000000 10111101 00100010 01100010 10010101 '
                    '10010101 10111111 01111001 11011111 10101010 10101100 11100100 00110011 10000110 10010110',
                'intervals':
                    [(0, 0), (1, 195), (141, -171), (95, 282), (73, 110), (-283, 275), (-177, 351), (345, 399),
                     (5, None)],
            },
            {
                'id':
                    2,
                'array_size':
                    800,
                'string':
                    '10111001000011110110010011010110000000000011101011011101010110010100110000110011011100001111101010'
                    '10001010001100010110100111101000110101110011110111011010010001101011110001000100001101111010001000'
                    '00110011011111010011001110010111101111100100010110100110110100101000010010101111011110000001111110'
                    '10110100010111111101101111101101111100111011100111100011111011100101011000100110011000010110011101'
                    '10001111011010000101000101000111110011001101110111010111011111110010001101101001100000001010111111'
                    '11011000101011011000101001000010011111000100111111010100100010111000010100001101110111111100111010'
                    '00111111001010111111111010011001100000110111100111100110001001001100010010000111111101011100011101'
                    '01100100101101100011001001111111010110111010010001101010001110011110110010110000010011011110110101'
                    '0000110101110010',
                'string_spaced':
                    '10111001 00001111 01100100 11010110 00000000 00111010 11011101 01011001 01001100 00110011 '
                    '01110000 11111010 10100010 10001100 01011010 01111010 00110101 11001111 01110110 10010001 '
                    '10101111 00010001 00001101 11101000 10000011 00110111 11010011 00111001 01111011 11100100 '
                    '01011010 01101101 00101000 01001010 11110111 10000001 11111010 11010001 01111111 01101111 '
                    '10110111 11001110 11100111 10001111 10111001 01011000 10011001 10000101 10011101 10001111 '
                    '01101000 01010001 01000111 11001100 11011101 11010111 01111111 00100011 01101001 10000000 '
                    '10101111 11110110 00101011 01100010 10010000 10011111 00010011 11110101 00100010 11100001 '
                    '01000011 01110111 11110011 10100011 11110010 10111111 11101001 10011000 00110111 10011110 '
                    '01100010 01001100 01001000 01111111 01011100 01110101 10010010 11011000 11001001 11111101 '
                    '01101110 10010001 10101000 11100111 10110010 11000001 00110111 10110101 00001101 01110010',
                'intervals':
                    [(0, 0), (1, 195), (-448, 567), (-614, -361), (30, 779), (-371, 659), (-492, -144), (-384, 799),
                     (5, None)],
            },
        ]

    def __define_as_formatted_string_data(self):
        self.as_formatted_string_data = [
            # TODO add more
            {
                'id':
                    0,
                'array_size':
                    200,
                'mock_return':
                    '1000101100111110011011011011101100010011101101111011110110010101001111111111000101100010101000000'
                    '0101111000101101001100001010001000001110110110000110110100011100111101111111111000100110100101110'
                    '110110',
                'string_headed':
                    '0        1        2        3        4        5        6        7        8        9       \n'
                    '10001011 00111110 01101101 10111011 00010011 10110111 10111101 10010101 00111111 11110001\n'
                    '10       11       12       13       14       15       16       17       18       19      \n'
                    '01100010 10100000 00101111 00010110 10011000 01010001 00000111 01101100 00110110 10001110\n'
                    '20       21       22       23       24      \n'
                    '01111011 11111111 00010011 01001011 10110110',
                'string':
                    '10001011 00111110 01101101 10111011 00010011 10110111 10111101 10010101 00111111 11110001\n'
                    '01100010 10100000 00101111 00010110 10011000 01010001 00000111 01101100 00110110 10001110\n'
                    '01111011 11111111 00010011 01001011 10110110',
                'intervals':
                    {
                        (0, 0):
                            '',
                        (12, 125):
                            '1        2        3        4        5        6        7        8        9        '
                            '10      \n'
                            '    1110 01101101 10111011 00010011 10110111 10111101 10010101 00111111 11110001 '
                            '01100010\n'
                            '11       12       13       14       15      \n'
                            '10100000 00101111 00010110 10011000 01010',
                        (-83, 199):
                            '14       15       16       17       18       19       20       21       22       '
                            '23      \n'
                            '     000 01010001 00000111 01101100 00110110 10001110 01111011 11111111 00010011 '
                            '01001011\n'
                            '24      \n'
                            '1011011',
                        (-93, -92):
                            '13      \n'
                            '   1',
                    },
                'bytes_in_row':
                    {
                        2:
                            '0        1       \n'
                            '10001011 00111110\n'
                            '2        3       \n'
                            '01101101 10111011\n'
                            '4        5       \n'
                            '00010011 10110111\n'
                            '6        7       \n'
                            '10111101 10010101\n'
                            '8        9       \n'
                            '00111111 11110001\n'
                            '10       11      \n'
                            '01100010 10100000\n'
                            '12       13      \n'
                            '00101111 00010110\n'
                            '14       15      \n'
                            '10011000 01010001\n'
                            '16       17      \n'
                            '00000111 01101100\n'
                            '18       19      \n'
                            '00110110 10001110\n'
                            '20       21      \n'
                            '01111011 11111111\n'
                            '22       23      \n'
                            '00010011 01001011\n'
                            '24      \n'
                            '10110110',
                        8:
                            '0        1        2        3        4        5        6        7       \n'
                            '10001011 00111110 01101101 10111011 00010011 10110111 10111101 10010101\n'
                            '8        9        10       11       12       13       14       15      \n'
                            '00111111 11110001 01100010 10100000 00101111 00010110 10011000 01010001\n'
                            '16       17       18       19       20       21       22       23      \n'
                            '00000111 01101100 00110110 10001110 01111011 11111111 00010011 01001011\n'
                            '24      \n'
                            '10110110',
                        15:
                            '0        1        2        3        4        5        6        7        8        '
                            '9        10       11       12       13       14      \n'
                            '10001011 00111110 01101101 10111011 00010011 10110111 10111101 10010101 00111111 '
                            '11110001 01100010 10100000 00101111 00010110 10011000\n'
                            '15       16       17       18       19       20       21       22       23       '
                            '24      \n'
                            '01010001 00000111 01101100 00110110 10001110 01111011 11111111 00010011 01001011 '
                            '10110110',
                        20:
                            '0        1        2        3        4        5        6        7        8        '
                            '9        10       11       12       13       14       15       16       17       '
                            '18       19      \n'
                            '10001011 00111110 01101101 10111011 00010011 10110111 10111101 10010101 00111111 '
                            '11110001 01100010 10100000 00101111 00010110 10011000 01010001 00000111 01101100 '
                            '00110110 10001110\n'
                            '20       21       22       23       24      \n'
                            '01111011 11111111 00010011 01001011 10110110',
                    },
            },
        ]

    @property
    def as_string__no_indices_no_space__returns_string_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array_size, expected string without spaces, ByteChunkSize), ...]
        """
        parameters = [(entry['id'], entry['array_size'], entry['string']) for entry in self._as_string_data]
        parameters = itertools.product(parameters, self._byte_chunk_sizes)
        parameters = [(a, b, c, d) for ((a, b, c), d) in list(parameters)]

        return parameters

    @property
    def as_string__no_indices_with_space__returns_string_with_byte_chunks_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array_length, expected string with spaces, ByteChunkSize), ...]
        """
        parameters = [(entry['id'], entry['array_size'], entry['string_spaced']) for entry in self._as_string_data]
        parameters = itertools.product(parameters, self._byte_chunk_sizes)
        parameters = [(a, b, c, d) for ((a, b, c), d) in list(parameters)]

        return parameters

    @property
    def as_string__with_indices_no_space__returns_indexed_string_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array_size, expected string without spaces, One indices pair, ByteChunkSize), ...]
        """
        parameters = [
            itertools.product(
                [(entry['id'], entry['array_size'], entry['string'])],
                entry['intervals']
            ) for entry in self._as_string_data]
        parameters = [(a, b, c, d) for product in parameters for ((a, b, c), d) in list(product)]
        parameters = itertools.product(parameters, self._byte_chunk_sizes)
        parameters = [(a, b, c, d, e) for ((a, b, c, d), e) in list(parameters)]
        parameters = [(a, b, c[d[0]: d[1]], d, e) for (a, b, c, d, e) in parameters]

        return parameters

    @property
    def as_string__with_indices_with_space__returns_indexed_string_with_byte_chunks_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array_size, expected string with spaces, One indices pair, ByteChunkSize), ...]
        """
        parameters = [
            itertools.product(
                [(entry['id'], entry['array_size'], entry['string_spaced'])],
                entry['intervals']
            ) for entry in self._as_string_data]
        parameters = [(a, b, c, d) for product in parameters for ((a, b, c), d) in list(product)]
        parameters = itertools.product(parameters, self._byte_chunk_sizes)
        parameters = [(a, b, c, d, e) for ((a, b, c, d), e) in list(parameters)]
        # Approximation of indices is enough
        parameters = [(a, b, c[d[0]: d[1]], d, e) for (a, b, c, d, e) in parameters]

        return parameters

    @property
    def as_formatted_string__default_parameters__returns_expected_formatted_string_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array_size, array_to_bit_string return, expected string, ByteChunkSize), ...]
        """
        parameters = [(entry['id'], entry['array_size'], entry['mock_return'], entry['string_headed']) for entry in
                      self.as_formatted_string_data]
        parameters = itertools.product(parameters, self._byte_chunk_sizes)
        parameters = [(a, b, c, d, e) for ((a, b, c, d), e) in list(parameters)]

        return parameters

    @property
    def as_formatted_string__with_indices__returns_expected_formatted_string_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array_size, array_to_bit_string return, indices, expected string, ByteChunkSize), ...]
        """
        parameters = [
            itertools.product(
                [(entry['id'], entry['array_size'], entry['mock_return'])],
                list(entry['intervals'].items())
            ) for entry in self.as_formatted_string_data]
        parameters = [(a, b, c, d[0], d[1]) for product in parameters for ((a, b, c), d) in list(product)]
        parameters = itertools.product(parameters, self._byte_chunk_sizes)
        parameters = [(a, b, c, d, e, f) for ((a, b, c, d, e), f) in list(parameters)]

        return parameters

    @property
    def as_formatted_string__changed_bytes_in_row__returns_expected_formatted_string_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array_size, array_to_bit_string return, bytes_in_row, expected string, ByteChunkSize), ...]
        """
        parameters = [
            itertools.product(
                [(entry['id'], entry['array_size'], entry['mock_return'])],
                list(entry['bytes_in_row'].items()),
                self._byte_chunk_sizes
            )
            for entry in self.as_formatted_string_data
        ]
        parameters = [(a, b, c, d[0], d[1], e) for product in parameters for ((a, b, c), d, e) in list(product)]

        return parameters

    @property
    def as_formatted_string__invalid_bytes_in_row__raises_value_error_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array_size, array_to_bit_string return, invalid bytes_in_row, ByteChunkSize), ...]
        """
        parameters = [(entry['id'], entry['array_size'], entry['mock_return']) for entry in
                      self.as_formatted_string_data]
        parameters = itertools.product(parameters, self._as_formatted_string_invalid_bytes_in_row,
                                       self._byte_chunk_sizes)
        parameters = [(a, b, c, d, e) for ((a, b, c), d, e) in list(parameters)]

        return parameters

    @property
    def as_formatted_string__without_header__returns_expected_formatted_string_data(self):
        """
        Gets the parameter data for the specified test.
        :return: [(id, array_size, array_to_bit_string return, expected string without header, ByteChunkSize), ...]
        """
        parameters = [(entry['id'], entry['array_size'], entry['mock_return'], entry['string']) for entry in
                      self.as_formatted_string_data]
        parameters = itertools.product(parameters, self._byte_chunk_sizes)
        parameters = [(a, b, c, d, e) for ((a, b, c, d), e) in list(parameters)]

        return parameters


if __name__ == '__main__':
    provider = BitArrayTestData()
    data = provider.as_formatted_string__changed_bytes_in_row__returns_expected_formatted_string_data
    print('-----------')
    print(len(data))
    for i in range(10):
        print(data[i])
