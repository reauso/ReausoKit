from unittest import TestCase

from rkit.list import list_product, list_quotient


class ListMathTests(TestCase):

    # Tests for list_product
    def test_list_product_GivenPositiveNumbers_ReturnsCorrectProduct(self):
        self.assertEqual(list_product([2, 3, 4]), 24)  # 2 * 3 * 4 = 24

    def test_list_product_GivenNegativeNumbers_ReturnsCorrectProduct(self):
        self.assertEqual(list_product([1, -1, 2, -2]), 4)  # 1 * -1 * 2 * -2 = 4

    def test_list_product_GivenEmptyList_ReturnsStartValue(self):
        self.assertEqual(list_product([]), 1.0)  # Empty list should return start value

    def test_list_product_GivenStartValue_MultipliesCorrectly(self):
        self.assertEqual(list_product([2, 3], start=2), 12)  # 2 * 2 * 3 = 12

    def test_list_product_GivenListContainingZero_ReturnsZero(self):
        self.assertEqual(list_product([0, 1, 2]), 0)  # Multiplying by zero results in zero

    def test_list_product_GivenDecimals_ReturnsCorrectProduct(self):
        self.assertEqual(list_product([0.5, 0.2, 10]), 1.0)  # 0.5 * 0.2 * 10 = 1.0

    # Tests for list_quotient
    def test_list_quotient_GivenPositiveNumbers_ReturnsCorrectQuotient(self):
        self.assertEqual(list_quotient([2, 2]), 0.25)  # 1.0 / 2 / 2 = 0.25

    def test_list_quotient_GivenStartValue_DividesCorrectly(self):
        self.assertEqual(list_quotient([5], start=10), 2.0)  # 10 / 5 = 2.0

    def test_list_quotient_GivenAllOnes_ReturnsOne(self):
        self.assertEqual(list_quotient([1, 1, 1]), 1.0)  # 1 / 1 / 1 = 1.0

    def test_list_quotient_GivenLargeNumber_ReturnsCorrectQuotient(self):
        self.assertEqual(list_quotient([10], start=100), 10.0)  # 100 / 10 = 10.0

    def test_list_quotient_GivenDecimals_ReturnsCorrectQuotient(self):
        self.assertAlmostEqual(list_quotient([0.5, 0.2]), 10.0)  # 1.0 / 0.5 / 0.2 = 10.0

    def test_list_quotient_GivenZeroInList_RaisesZeroDivisionError(self):
        with self.assertRaises(ZeroDivisionError):
            list_quotient([0, 1, 2])  # 1.0 / 0 should raise ZeroDivisionError
