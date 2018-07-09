from unittest import TestCase
import pandas.util.testing as pdt

from pyutil.influx.client import Client
from pyutil.sql.interfaces.symbols.strategy import Strategy
from test.config import test_portfolio, resource


class TestStrategy(TestCase):
    @classmethod
    def setUpClass(cls):
        with open(resource("source.py"), "r") as f:
            cls.s = Strategy(name="Peter", source=f.read(), active=True)

        # this is a way to compute a portfolio from the source code given in source.py
        config = cls.s.configuration(reader=None)
        portfolio = config.portfolio

        cls.client = Client(host='test-influxdb', database="test-strategy")
        cls.s.upsert(client=cls.client, portfolio=portfolio)

        #cls.p.upsert_influx(client=cls.client, portfolio=test_portfolio())

    @classmethod
    def tearDownClass(cls):
        cls.client.drop_database(dbname="test-strategy")

    def test_upsert(self):
        p = self.s.portfolio(client=self.client)
        pdt.assert_frame_equal(p.weights, test_portfolio().weights, check_names=False)
        pdt.assert_frame_equal(p.prices, test_portfolio().prices, check_names=False)

        self.s.upsert(client=self.client, portfolio=5*test_portfolio().tail(10), days=10)
        p = self.s.portfolio(client=self.client)
        x = p.weights.tail(12).sum(axis=1)
        self.assertAlmostEqual(x["2015-04-08"], 0.305048, places=5)
        self.assertAlmostEqual(x["2015-04-13"], 1.486652, places=5)
