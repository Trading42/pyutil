import pandas as pd
import pandas.util.testing as pdt
from pyutil.portfolio.portfolio import build
from test.config import test_portfolio, read_frame
from unittest import TestCase

portfolio = test_portfolio()


class TestPortfolio(TestCase):
    def test_leverage(self):
        self.assertAlmostEqual(portfolio.leverage[pd.Timestamp("2013-07-19")], 0.25505730106555635, places=5)

    def test_nav(self):
        self.assertAlmostEqual(portfolio.nav.series[pd.Timestamp("2013-07-19")], 0.9849066065468487, places=5)

    def test_assets(self):
        self.assertSetEqual(set(portfolio.assets),
                            {'A','B','C','D','E','F','G'})

    def test_summary(self):
        self.assertAlmostEqual(portfolio.summary()[100]["Max Drawdown"], 1.7524809688827636, places=5)

    def test_index(self):
        pdt.assert_index_equal(portfolio.index, portfolio.prices.index)

    def test_asset_return(self):
        pdt.assert_frame_equal(portfolio.prices.pct_change(), portfolio.asset_returns)

    def test_truncate(self):
        self.assertEqual(portfolio.truncate(before=pd.Timestamp("2013-01-08")).index[0], pd.Timestamp("2013-01-08"))

    def test_top_flop(self):
        x = portfolio.top_flop(day_final=pd.Timestamp("2015-01-01"))
        self.assertAlmostEqual(x["Value"].values[16], 0.00025637273414469419, places=5)

    def test_tail(self):
        x = portfolio.tail(5)
        self.assertEqual(len(x.index), 5)
        self.assertEqual(x.index[0], pd.Timestamp("2015-04-16"))

    def test_snapshot(self):
        x = portfolio.snapshot()
        pdt.assert_frame_equal(x, read_frame("snapshot.csv"))

    def test_sector_weights(self):
        x = portfolio.sector_weights(pd.Series({"A": "A", "B": "A", "C": "B", "D": "B",
       "E": "C", "F": "C", "G": "C"}))

        pdt.assert_frame_equal(x.head(10), read_frame("sector_weights.csv", parse_dates=True))

    def test_position(self):
        x = 1e6*portfolio.position
        self.assertAlmostEqual(x["A"][pd.Timestamp("2015-04-22")], 60.191699988670969, places=5)

    def test_cash(self):
        self.assertAlmostEqual(portfolio.cash[pd.Timestamp("2015-04-22")], 0.69102612448658074, places=5)

    def test_build(self):
        prices = read_frame("price.csv")
        weights = pd.DataFrame(index=[prices.index[5]], data=0.1, columns=prices.keys())
        portfolio = build(prices, weights)

        self.assertEqual(portfolio.index[5], pd.Timestamp('2013-01-08'))
        self.assertAlmostEqual(portfolio.weights["B"][pd.Timestamp('2013-01-08')], 0.1, places=5)

    def test_build_portfolio(self):
        prices = pd.DataFrame(columns=["A", "B"], index=[1, 2, 3], data=[[1000, 1000], [1500, 1500], [2000, 2000]])
        weights = pd.DataFrame(columns=["A", "B"], index=[1], data=[[0.25, 0.25]])

        portfolio = build(prices=prices, weights=weights)

        pdt.assert_frame_equal(prices, portfolio.prices)

        position = pd.DataFrame(columns=["A", "B"], index=[1, 2, 3], data=0.00025)
        pdt.assert_frame_equal(portfolio.position, position)

    def test_mul(self):
        pdt.assert_frame_equal(2 * portfolio.weights, (2 * portfolio).weights)
