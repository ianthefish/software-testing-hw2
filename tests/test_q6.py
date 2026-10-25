import unittest

from calculator import Calculator


class TestAgenticContract(unittest.TestCase):
    def test_modulo_and_power_contract(self):
        """One test method defines the complete reviewed integer-input contract."""
        calc = Calculator()
        cases = [
            ("modulo", 7, 3, 1, int),
            ("modulo", -7, 3, 2, int),
            ("modulo", 7, -3, -2, int),
            ("modulo", -7, -3, -1, int),
            ("modulo", 0, 3, 0, int),
            ("modulo", 6, 3, 0, int),
            ("power", 2, 3, 8, int),
            ("power", -2, 3, -8, int),
            ("power", -2, 4, 16, int),
            ("power", 5, 0, 1, int),
            ("power", 0, 0, 1, int),
            ("power", 2, -3, 0.125, float),
            ("power", -2, -3, -0.125, float),
            ("power", 0, 3, 0, int),
        ]
        for operation, a, b, expected, expected_type in cases:
            with self.subTest(operation=operation, a=a, b=b):
                result = getattr(calc, operation)(a, b)
                self.assertEqual(result, expected)
                self.assertIs(type(result), expected_type)

        for operation, a, b in [("modulo", 7, 0), ("modulo", 0, 0), ("power", 0, -1)]:
            with self.subTest(operation=operation, a=a, b=b, raises="ZeroDivisionError"):
                with self.assertRaises(ZeroDivisionError):
                    getattr(calc, operation)(a, b)


if __name__ == "__main__":
    unittest.main()
