from unittest import TestCase

import pandas as pd
import pandas.util.testing as pdt

from pyutil.sql.interfaces.symbol import Strategy, Symbol, Portfolio
from test.config import test_portfolio, resource


class TestModels(TestCase):

    def test_strategy(self):
        with open(resource("source.py"), "r") as f:
            s = Strategy(name="peter", source=f.read(), active=True)
            # No, this doesn't work!
            portfolio = s.compute_portfolio(reader=None)

            assets = {asset: Symbol(bloomberg_symbol=asset) for asset in portfolio.assets}

            p = Portfolio(name="test", strategy=s)
            print(portfolio)
            # upsert the portfolio, make sure you append the symbols!!!
            #for asset in assets.values():
            #    p.symbols.append(asset)

            p.upsert(portfolio, assets=assets)


            #for asset in portfolio.assets:
            #    symbol = Symbol(bloomberg_symbol=asset)
            #    p.symbols.append(symbol)
            #    p.upsert_price(symbol=symbol, data=portfolio.prices[asset])
            #    p.upsert_weight(symbol=symbol, data=portfolio.weights[asset])


            #self.assertIsNotNone(s._portfolio)
            #self.assertIsNotNone(s.portfolio)


            # pdt.assert_frame_equal(s._portfolio.weight, test_portfolio().weights)
            # pdt.assert_frame_equal(s._portfolio.price, test_portfolio().prices)
            #
            self.assertEqual(s._portfolio.last_valid, pd.Timestamp("2015-04-22"))

            # self.assertListEqual(s.assets, ['A', 'B', 'C', 'D', 'E', 'F', 'G'])
            #
            # upsert an existing portfolio

            x = test_portfolio().tail(10)
            # double the weights for the last 5 days of the existing portfolio
            #x = s.upsert(portfolio=2*x, days=5)

            # # check for the jump in leverage
            # self.assertAlmostEqual(x.leverage.loc["2015-04-16"], 0.3121538556, places=7)
            # self.assertAlmostEqual(x.leverage.loc["2015-04-17"], 0.6213015319, places=7)
            #
            # s = Strategy(name="maffay")
            # x=s.upsert(portfolio=test_portfolio())
            # self.assertAlmostEqual(x.leverage.loc["2015-04-16"], 0.3121538556, places=7)
            # self.assertAlmostEqual(x.leverage.loc["2015-04-17"], 0.3106507659, places=7)

    # def test_portfolio(self):
    #     portfolio = test_portfolio()
    #
    #     p = PortfolioSQL(name="test")
    #     self.assertTrue(p.empty)
    #     p.upsert(portfolio=portfolio)
    #     self.assertFalse(p.empty)
    #
    #     pdt.assert_frame_equal(p.price, test_portfolio().prices)
    #     pdt.assert_frame_equal(p.weight, test_portfolio().weights)
    #     self.assertEqual(p.assets, test_portfolio().assets)
    #     self.assertEqual(p.last_valid, test_portfolio().index[-1])
    #
    #     self.assertAlmostEqual(p.nav.sharpe_ratio(), 0.1127990962306739, places=10)
    #
    #     # test the truncation
    #     p1 = portfolio.truncate(after=pd.Timestamp("2015-01-01") - pd.DateOffset(seconds=1))
    #     pp = PortfolioSQL(name="wurst")
    #
    #     pp.upsert(portfolio=test_portfolio().truncate(after=pd.Timestamp("2015-02-01")))
    #     self.assertEqual(p1.index[-1], pd.Timestamp("2014-12-31"))
    #     p2 = portfolio.truncate(before=pd.Timestamp("2015-01-01").date())
    #
    #     pp.upsert(portfolio=p2)
    #     pdt.assert_frame_equal(pp.weight, test_portfolio().weights)
    #
    # def test_portfolio_sector(self):
    #     portfolio = test_portfolio()
    #     p = PortfolioSQL(name="test")
    #     self.assertIsNone(p.last_valid)
    #
    #     p.upsert(portfolio=portfolio)
    #     symbolmap=pd.Series({"A": "A", "B": "A", "C": "B", "D": "B", "E": "C", "F": "C", "G": "C"})
    #     x = p.sector(map=symbolmap, total=True)
    #     pdt.assert_frame_equal(x.head(10), read_frame("sector_weights.csv", parse_dates=True))
    #
    # def test_portfolio_new(self):
    #     p = Portfolio(name="test")
    #     self.assertTrue(p.empty)
    #     self.assertIsNone(p.last_valid)
    #
    #     s = Symbol(bloomberg_symbol="A", group=SymbolType.equities, internal="A internal")
    #     p.symbols.append(s)
    #
    #     p.upsert_weight(symbol=s, data={2: 0.5, 3: 0.5})
    #     p.upsert_price(symbol=s, data={2: 10.0, 3: 12.0})
    #
    #     #print(p.portfolio)
    #     for s in p.symbols:
    #         print(s.group.name)
    #
    #     print(p.weight)
    #     print(p.price)
    #     print(type(p.assets2[0]))
    #
    #
    #     self.assertEqual(p.last_valid, 3)
    #     print(p.sector)
