import pandas as pd

from pyutil.performance.summary import fromNav
from pyutil.sql.interfaces.symbols.portfolio import Portfolio, Portfolios
from pyutil.sql.interfaces.symbols.symbol import Symbol, Symbols
from pyutil.sql.session import session as sss
from pyutil.sql.util import to_pandas, parse
from pyutil.portfolio.portfolio import Portfolio as PP


class Database(object):
    def __init__(self, session=None):
        self.__session = session or sss(db="symbols")

    #@property
    #def symbols(self):
    #    return Symbols(self.__session.query(Symbol))

    #@property
    #def portfolios(self):
    #    return Portfolios(self.__session.query(Portfolio))

    @property
    def nav(self):
        x = pd.read_sql_query("SELECT * FROM v_portfolio_nav", con=self.__session.bind, index_col="name")["data"]
        return x.apply(lambda x: fromNav(to_pandas(x)))

    @property
    def sector(self, total=False):
        frame = pd.read_sql_query("SELECT * FROM v_portfolio_sector", con=self.__session.bind, index_col=["name", "symbol", "group"])["data"]
        frame.apply(to_pandas).groupby(level=["name", "group"], axis=0).sum().ffill(axis=1)
        if total:
            frame["total"] = frame.sum(axis=1)
        return frame

    @property
    def mtd(self):
        frame = self.nav.apply(lambda x: fromNav(x).mtd_series, axis=1)
        frame = frame.rename(columns=lambda x: x.strftime("%b %d"))
        frame["total"] = (frame + 1).prod(axis=1) - 1
        return frame

    @property
    def ytd(self):
        frame = self.nav.apply(lambda x: fromNav(x).ytd_series, axis=1)
        frame = frame.rename(columns=lambda x: x.strftime("%b"))
        frame["total"] = (frame + 1).prod(axis=1) - 1
        return frame

    def recent(self, n=15):
        frame = self.nav.apply(lambda x: fromNav(x).recent(n=n), axis=1).iloc[:, -n:]
        frame = frame.rename(columns=lambda x: x.strftime("%b %d"))
        frame["total"] = (frame + 1).prod(axis=1) - 1
        return frame

    @property
    def period_returns(self):
        return self.nav.apply(lambda x: fromNav(x).period_returns, axis=1)


    @property
    def performance(self):
        return self.nav.apply(lambda x: fromNav(x).summary(), axis=1)

    def frames(self, total=False, n=15):
        return {"recent": self.recent(n=n),
                "ytd": self.ytd,
                "mtd": self.mtd,
                "sector": self.sector(total=total),
                "periods": self.period_returns,
                "performance": self.performance}

    @property
    def assets(self):
        frame = pd.read_sql_query("SELECT * FROM v_assets", con=self.__session.bind, index_col=["name", "group", "internal", "field"])["value"]
        print(frame)
        assert False

    def portfolio(self, name):
        x = pd.read_sql_query("SELECT * FROM v_portfolio_2 where name=%(name)s", params={"name": name}, con=self.__session.bind, index_col=["timeseries", "symbol"])["data"]
        x = x.apply(to_pandas)
        return PP(prices=x.loc["price"].transpose(), weights=x.loc["weight"].transpose())

    def state(self, name):
        portfolio = self.portfolio(name=name)
        assets = self.assets


    @property
    def reference_symbols(self):
        reference = pd.read_sql_query(sql="SELECT * FROM v_reference_symbols", con=self.__session.bind,
                                      index_col=["symbol", "field"])
        reference["value"] = reference[['content', 'result']].apply(lambda x: parse(x[0], x[1]), axis=1)
        return reference.unstack()

    @property
    def prices(self):
        prices = pd.read_sql_query(sql="SELECT * FROM v_symbols", con=self.__session.bind, index_col="name")["data"]
        prices = prices.apply(to_pandas).transpose()
        prices.index.names = ["Date"]
        return prices

    def symbol(self, name):
        # TODO

    def portfolio(self, name):
        # TODO
