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


if __name__ == "__main__":
    unittest.main()
