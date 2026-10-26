import unittest

from calculator import Calculator


class TestCalculator(unittest.TestCase):
    def test_add(self):
        calc = Calculator()
        self.assertEqual(calc.add(2, 3), 5)

    def test_subtract_integers(self):
        calc = Calculator()
        for a, b, expected in [(9, 4, 5), (4, 9, -5), (-7, 3, -10),
                               (7, -3, 10), (-7, -3, -4), (0, 0, 0)]:
            with self.subTest(a=a, b=b):
                self.assertEqual(calc.subtract(a, b), expected)

    def test_multiply_integers(self):
        calc = Calculator()
        for a, b, expected in [(6, 7, 42), (-6, 7, -42), (6, -7, -42),
                               (-6, -7, 42), (0, 7, 0), (7, 0, 0)]:
            with self.subTest(a=a, b=b):
                self.assertEqual(calc.multiply(a, b), expected)

    def test_divide_returns_float(self):
        calc = Calculator()
        for a, b, expected in [(7, 2, 3.5), (8, 2, 4.0), (-7, 2, -3.5),
                               (7, -2, -3.5), (-7, -2, 3.5), (0, 5, 0.0)]:
            with self.subTest(a=a, b=b):
                result = calc.divide(a, b)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, float)

    def test_divide_by_zero_raises_value_error(self):
        calc = Calculator()
        with self.assertRaises(ValueError):
            calc.divide(7, 0)


if __name__ == "__main__":
    unittest.main()
