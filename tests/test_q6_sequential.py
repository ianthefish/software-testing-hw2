import unittest

from calculator import Calculator


class TestSequentialQ6(unittest.TestCase):
    def test_modulo_negative_dividend(self):
        self.assertEqual(Calculator().modulo(-7, 3), 2)


if __name__ == "__main__":
    unittest.main()
