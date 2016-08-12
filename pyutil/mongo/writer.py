import pandas as pd
import logging
from pyutil.mongo.aux import flatten, series2dict

from pyutil.mongo.reader import _ArchiveReader
from pyutil.nav.nav import Nav


class _ArchiveWriter(_ArchiveReader):
    def __init__(self, db, logger=None):
        super(_ArchiveWriter, self).__init__(db)
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("Archive at {0}".format(db))
        self.__db = db

    def update_asset(self, asset, ts, name="PX_LAST"):
        # this update is cheap when ts is short!
        self.logger.debug("Asset: {0}, Name of ts: {1}, Len of ts: {2}".format(asset, name, len(ts.dropna().index)))

        # look for the asset in database
        if not ts.empty:
            # asset already in database
            m = {"_id": asset}
            if self.__db.assets.find_one(m):
                self.__db.assets.update(m, flatten(name, ts), upsert=True)
            else:
                self.__db.assets.update(m, {name: series2dict(ts)}, upsert=True)

    def update_portfolio(self, key, portfolio, group, n=10, comment=""):
        self.logger.debug("Key {0}, Group {1}".format(key, group))

        q = {"_id": key}

        if key in self.portfolios.keys():
            offset = self.portfolios[key].index[-1] - pd.offsets.BDay(n=n)
            self.logger.debug("Offset {0}".format(offset))
            portfolio = portfolio.truncate(before=offset)

            self.__db.strategy.update(q, flatten("weight", portfolio.weights), upsert=True)
            self.__db.strategy.update(q, flatten("price", portfolio.prices), upsert=True)
            self.__db.strategy.update(q, flatten("returns", portfolio.nav.returns.ix[1:]), upsert=True)
        else:
            self.__db.strategy.update(q, portfolio.to_json(), upsert=True)

        now = pd.Timestamp("now")
        self.__db.strategy.update(q, {"$set": {"group": group, "time": now, "comment": comment}}, upsert=True)

    def update_symbols(self, frame):
        self.logger.debug("Update reference data with:\n{0}".format(frame.head(3)))
        for index, row in frame.iterrows():
            self.__db.symbol.update({"_id": index}, {"$set": row.to_dict()}, upsert=True)

    def update_rtn(self, nav, name, today=pd.Timestamp("today")):
        n = Nav(nav)
        for a in n.returns.index:
            assert a.weekday() <= 4

        if self.read_nav(name):
            date = today.date() + pd.offsets.MonthBegin(n=-1)
            ts = n.returns.truncate(before=date)
        else:
            ts = n.returns

        ts = ts.dropna()

        if not ts.empty:
            m = {"_id": name}
            self.__db.fact.update(m, {"$set": m}, upsert=True)
            self.__db.fact.update(m, flatten("rtn", ts), upsert=True)

    def update_frame(self, name, frame):
        frame = frame.to_json(orient="split")
        self.__db.free.update({"_id": name}, {"_id": name, "data": frame}, upsert=True)
