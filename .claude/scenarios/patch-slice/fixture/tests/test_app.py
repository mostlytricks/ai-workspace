"""Baseline suite - GREEN against the buggy app.py, because nothing asserts
the clamp yet. That is exactly how the bug survived: untested behavior.
The patch adds test_clamp_over_100 (the graduated scenario) alongside the fix."""
import unittest

from app import apply_discount


class TestApplyDiscount(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(apply_discount(100, 20), 80)

    def test_zero_pct(self):
        self.assertEqual(apply_discount(100, 0), 100)


if __name__ == "__main__":
    unittest.main()
