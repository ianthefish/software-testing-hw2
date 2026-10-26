import unittest

from calculator import Calculator


class TestSequentialQ6(unittest.TestCase):
    def test_modulo_negative_dividend(self):
        self.assertEqual(Calculator().modulo(-7, 3), 2)

    def test_power_negative_exponent(self):
        result = Calculator().power(2, -3)
        self.assertEqual(result, 0.125)
        self.assertIs(type(result), float)


if __name__ == "__main__":
    unittest.main()
