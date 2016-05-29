import pandas as pd
import logging
from pyutil.nav.nav import Nav

from pyutil.portfolio.portfolio import Portfolio
from pyutil.timeseries.timeseries import adjust


def _str2stamp(frame):
    return frame.rename(index={a: pd.Timestamp(a) for a in frame.index})


def _cursor2frame(cursor, name):
    d = {a["id"]: a[name] for a in cursor if name in a.keys()}
    return _str2stamp(pd.DataFrame(d))


class _Portfolios(object):
    def __init__(self, col):
        self.__col = col

    def items(self):
        return [(k, self[k]) for k in self.keys()]

    def keys(self):
        return {x["id"] for x in self.__col.find({}, {"id": 1})}

    # return a dictionary portfolio
    def __getitem__(self, item):
        def __f(frame):
            frame.index = [pd.Timestamp(x) for x in frame.index]
            return frame

        p = self.__col.find_one({"id": item}, {"id": 1, "price": 1, "weight": 1})
        if p:
            return Portfolio(prices=__f(pd.DataFrame(p["price"])), weights=__f(pd.DataFrame(p["weight"])))
        else:
            return None

    @property
    def strategies(self):
        portfolios = self.__col.find({}, {"id": 1, "group": 1, "time": 1, "comment": 1})
        d = {p["id"]: pd.Series({"group": p["group"], "time": p["time"], "comment": p["comment"]}) for p in portfolios}
        return pd.DataFrame(d).transpose()

    @property
    def nav(self):
        p = self.__col.find({}, {"id": 1, "returns": 1})
        return ((_cursor2frame(p, "returns") + 1.0).cumprod()).apply(adjust)


class _ArchiveReader(object):
    def __init__(self, db, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("Archive at {0}".format(db))
        self.__db = db
        self.__portfolio = _Portfolios(db.strat_new)

    def __repr__(self):
        return "Reader for {0}".format(self.__db)

    @property
    def portfolios(self):
        return self.__portfolio

    # bad idea to make history a property as we may have different names, e.g PX_LAST, PX_VOLUME, etc...
    def history(self, items=None, name="PX_LAST"):
        collection = self.__db.asset

        if items:
            p = collection.find({"id": {"$in": items}}, {"id": 1, name: 1})
        else:
            p = collection.find({}, {"id": 1, name: 1})

        return _cursor2frame(p, name)

    def history_series(self, item, name="PX_LAST"):
        return self.history(items=[item], name=name)[item]

    @property
    def symbols(self):
        f = pd.DataFrame({row["id"]: pd.Series(row) for row in self.__db.symbols.find({})}).transpose()
        return f.drop(["_id", "id"], axis=1)

    def read_nav(self, name):
        rtn = "d-rtn"
        a = self.__db.factsheet.find_one({"fee": 0.0, "name": name}, {rtn: 1})
        if a:
            y = _str2stamp(pd.Series(a[rtn]))
            return Nav((y + 1.0).cumprod())
        else:
            return None

    def read_frame(self, name=None):
        if name:
            a = self.__db.free.find_one({"name": name}, {"data": 1})
            return pd.read_json(a["data"], orient="split")
        else:
            return {p["name"]: pd.read_json(p["data"], orient="split") for p in self.__db.free.find()}