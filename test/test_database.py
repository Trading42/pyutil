from unittest import TestCase

import pandas as pd

from pyutil.data import Database
from pyutil.sql.base import Base
from pyutil.sql.interfaces.symbols.portfolio import Portfolio
from pyutil.sql.interfaces.symbols.strategy import Strategy
from pyutil.sql.interfaces.symbols.symbol import Symbol, SymbolType
from pyutil.sql.session import postgresql_db_test

import pandas.util.testing as pdt

from test.config import test_portfolio


class TestDatabase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.symbols = dict()
        for name in ["A", "B", "C"]:
            cls.symbols[name] = Symbol(name=name, group=SymbolType.equities)

        for name in ["D", "E", "F", "G"]:
            cls.symbols[name] = Symbol(name=name, group=SymbolType.fixed_income)

        session, connection_str = postgresql_db_test(base=Base)
        cls.database = Database(session=session)

        # this will add a portfolio, too!
        s = Strategy(name="Peter Maffay")
        s.upsert(portfolio=test_portfolio(), symbols=cls.symbols)

        for name, ts in test_portfolio().prices.items():
            cls.symbols[name].ts["PX_LAST"] = ts.dropna()

        session.add(s)
        session.commit()

    @classmethod
    def tearDownClass(cls):
        cls.database.close()

    def test_recent(self):
        frame = self.database.recent()
        self.assertEqual(frame["Apr 17"]["Peter Maffay"], "-0.17%")
        self.assertEqual(frame["total"]["Peter Maffay"], "1.12%")

    def test_mtd(self):
        frame = self.database.mtd()
        self.assertEqual(frame["Apr 17"]["Peter Maffay"], "-0.17%")
        self.assertEqual(frame["total"]["Peter Maffay"], "1.41%")

    def test_ytd(self):
        frame = self.database.ytd()
        print(frame)
        self.assertEqual(frame["04"]["Peter Maffay"], "1.41%")
        self.assertEqual(frame["total"]["Peter Maffay"], "2.17%")

    def test_session(self):
        self.assertIsNotNone(self.database.session)

    def test_symbols(self):
        self.assertEqual(self.database.symbols.count(), 7)
        self.assertEqual(self.database.symbol(name="A"), Symbol(name="A"))

    def test_portfolios(self):
        self.assertEqual(self.database.portfolios.count(), 1)
        self.assertEqual(self.database.portfolio(name="Peter Maffay"), Portfolio(name="Peter Maffay"))

    def test_strategies(self):
        self.assertEqual(self.database.strategies.count(), 1)
        self.assertEqual(self.database.strategy(name="Peter Maffay"), Strategy(name="Peter Maffay"))

    def test_nav(self):
        f = self.database.nav()
        #p = self.database.portfolio(name="Peter Maffay")
        pdt.assert_series_equal(f["Peter Maffay"], pd.Series(test_portfolio().nav), check_names=False)

    def test_sector(self):
        f = self.database.sector(total=False)
        frame = pd.DataFrame(index=["Peter Maffay"], columns=["equities", "fixed_income"], data=[[0.135671, 0.173303]])
        pdt.assert_frame_equal(f, frame)

    def test_reference(self):
        f = self.database.reference
        self.assertTrue(f.empty)

    def test_history(self):
        f = self.database.history(field="PX_LAST")
        pdt.assert_frame_equal(f, test_portfolio().prices)

    def test_nav_strategy(self):
        f = self.database.nav_strategy(name="Peter Maffay", creator="Thomas")
        self.assertIsInstance(f, dict)
        self.assertEqual(f["creator"], "Thomas")

    def test_nav_strategy_empty(self):
        pass


    def test_nav_symbol(self):
        f = self.database.nav_asset(name="A", creator="Thomas")
        self.assertIsInstance(f, dict)
        self.assertEqual(f["creator"], "Thomas")

    def test_nav_symbol_empty(self):
        pass

