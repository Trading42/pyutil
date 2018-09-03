from unittest import TestCase
from test.config import read_series

from pyutil.performance._var import _VaR


class TestVar(TestCase):
    def test_class(self):
        s = read_series("ts.csv", parse_dates=True)
        v = _VaR(s, alpha=0.99)
        self.assertAlmostEqual(100*v.cvar, 0.51218385609772821, places=10)
        self.assertAlmostEqual(100*v.var, 0.47550914363392316, places=10)