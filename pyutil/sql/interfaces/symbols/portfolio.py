from pyutil.performance.summary import fromNav
from pyutil.portfolio.portfolio import Portfolio as _Portfolio
from pyutil.sql.interfaces.products import ProductInterface


class Portfolio(ProductInterface):
    __mapper_args__ = {"polymorphic_identity": "portfolio"}

    def __init__(self, name):
        super().__init__(name)

    def last(self, client):
        return client.last(measurement="nav", field="nav", conditions={"name": self.name})

    def upsert_influx(self, client, portfolio):
        assert isinstance(portfolio, _Portfolio)
        client.write_portfolio(portfolio=portfolio, name=self.name)

        # it's important to recompute the entire portfolio here...
        p = self.portfolio_influx(client=client)

        # update the nav
        client.write_series(ts=p.nav.dropna(), field="nav", tags={"name": self.name}, measurement="nav")
        # update the leverage
        client.write_series(ts=p.leverage.dropna(), field="leverage", tags={"name": self.name}, measurement="leverage")

    def portfolio_influx(self, client):
        p, w = client.read_portfolio(name=self.name)
        print(p)
        print(w)
        #pp = client.read_series(measurement="portfolio", field="*", conditions={"name": self.name})
        #print(pp)
        return _Portfolio(prices=p, weights=w)

    def symbols_influx(self, client):
        return self.portfolio_influx(client=client).assets

    def portfolio(self, rename=False):
        # todo: export to flat files and delete...

        # does it work?
        """ this we need to read the old format """
        prices = self.frame("price")
        weights = self.frame("weight")

        if rename:
            prices.rename(columns=lambda x: x.name, inplace=True)
            weights.rename(columns=lambda x: x.name, inplace=True)

        return _Portfolio(prices=prices, weights=weights)

    def nav(self, client):
        return fromNav(client.read_series(field="nav", measurement="nav", conditions={"name": self.name}))

    def leverage(self, client):
        return client.read_series(field="leverage", measurement="leverage", conditions={"name": self.name})

    @staticmethod
    def nav_all(client):
        return client.read_series(measurement="nav", field="nav", tags=["name"], unstack=True)

    @staticmethod
    def leverage_all(client):
        return client.read_series(measurement="leverage", field="leverage", tags=["name"], unstack=True)
