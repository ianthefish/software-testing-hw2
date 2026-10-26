import itertools
import math
import random
import unittest

from calculator import Calculator


class TestMetamorphicRelations(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_add_subtract_inverse(self):
        for a, b in itertools.product(range(-25, 26), repeat=2):
            with self.subTest(a=a, b=b):
                self.assertEqual(self.calc.subtract(self.calc.add(a, b), b), a)

    def test_subtraction_antisymmetry(self):
        for a, b in itertools.product(range(-25, 26), repeat=2):
            with self.subTest(a=a, b=b):
                self.assertEqual(self.calc.subtract(a, b), -self.calc.subtract(b, a))

    def test_multiplication_distributes_over_addition(self):
        for a, b, c in itertools.product(range(-10, 11), repeat=3):
            with self.subTest(a=a, b=b, c=c):
                self.assertEqual(self.calc.multiply(a, self.calc.add(b, c)),
                                 self.calc.add(self.calc.multiply(a, b), self.calc.multiply(a, c)))

    def test_multiply_divide_inverse(self):
        for a, b in itertools.product(range(-25, 26), repeat=2):
            if b == 0:
                continue
            with self.subTest(a=a, b=b):
                recovered = self.calc.divide(self.calc.multiply(a, b), b)
                self.assertTrue(math.isclose(recovered, a, rel_tol=1e-12, abs_tol=1e-12))

    def test_seeded_large_integer_relations(self):
        rng = random.Random(20261025)
        for sample in range(1000):
            a, b, c = (rng.randint(-1_000_000, 1_000_000) for _ in range(3))
            with self.subTest(sample=sample, a=a, b=b, c=c):
                self.assertEqual(self.calc.subtract(self.calc.add(a, b), b), a)
                self.assertEqual(self.calc.subtract(a, b), -self.calc.subtract(b, a))
                self.assertEqual(self.calc.multiply(a, self.calc.add(b, c)),
                                 self.calc.add(self.calc.multiply(a, b), self.calc.multiply(a, c)))
                if b != 0:
                    recovered = self.calc.divide(self.calc.multiply(a, b), b)
                    self.assertTrue(math.isclose(recovered, a, rel_tol=1e-12, abs_tol=1e-12))


if __name__ == "__main__":
    unittest.main()
