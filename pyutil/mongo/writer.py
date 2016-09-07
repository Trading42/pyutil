import pandas as pd
import logging

from pyutil.mongo.reader import _ArchiveReader


def _flatten(name, ts):
    if isinstance(ts, pd.Series):
        a = ts.copy().dropna()
        a.index = ["{0}.{1}".format(name, t.strftime("%Y%m%d")) for t in a.index]
        return {"$set": a.to_dict()}

    if isinstance(ts, pd.DataFrame):
        a = ts.copy().stack().dropna()
        a.index = ["{0}.{1}.{2}".format(name, t[1], t[0].strftime("%Y%m%d")) for t in a.index]
        return {"$set": a.to_dict()}

    raise TypeError("ts is of type {0}".format(type(ts)))


def _series2dict(ts):
    return {"{0}".format(t.strftime("%Y%m%d")): v for t, v in ts.dropna().iteritems()}


class _ArchiveWriter(_ArchiveReader):
    def __init__(self, db, logger=None):
        super().__init__(db, logger)
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info("Archive (write-access) at {0}".format(db))
        self.__db = db

    def update_asset(self, asset, ts, name="PX_LAST"):
        # this update is cheap when ts is short!
        self.logger.debug("Asset: {0}, Name of ts: {1}, Len of ts: {2}".format(asset, name, len(ts.dropna().index)))

        # look for the asset in database
        if not ts.empty:
            # asset already in database
            m = {"_id": asset}
            if self.__db.assets.find_one(m):
                self.__db.assets.update(m, _flatten(name, ts), upsert=True)
            else:
                self.__db.assets.update(m, {name: _series2dict(ts)}, upsert=True)

    def update_assets(self, frame, name="PX_LAST"):
        for key in frame.keys():
            self.update_asset(key, ts=frame[key].dropna(), name=name)

    def update_portfolio(self, key, portfolio, group, n=10, comment=""):
        self.logger.info("Key {0}, Group {1}".format(key, group))

        q = {"_id": key}
        if key in self.portfolios.keys():
            offset = self.portfolios.index(key)[-1] - pd.offsets.BDay(n=n)
            self.logger.debug("Offset {0}".format(offset))
            portfolio = portfolio.truncate(before=offset)

            self.__db.strategy.update(q, _flatten("weight", portfolio.weights), upsert=True)
            self.__db.strategy.update(q, _flatten("price", portfolio.prices), upsert=True)
            self.__db.strategy.update(q, _flatten("returns", portfolio.nav.returns.ix[1:]), upsert=True)
        else:
            self.__db.strategy.update(q, portfolio.to_json(), upsert=True)

        now = pd.Timestamp("now")
        self.__db.strategy.update(q, {"$set": {"group": group, "time": now, "comment": comment}}, upsert=True)

    def update_symbols(self, frame):
        self.logger.debug("Update reference data with:\n{0}".format(frame.head(3)))
        for index, row in frame.iterrows():
            self.logger.info("Symbol: {0}".format(index))
            self.logger.debug("Properties: {0}".format(row.to_dict()))
            self.__db.symbol.update({"_id": index}, {"$set": row.to_dict()}, upsert=True)

    def update_rtn(self, ts, name):
        for a in ts.index:
            assert a.weekday() <= 4

        if not ts.empty:
            m = {"_id": name}
            self.__db.fact.update(m, _flatten("rtn", ts), upsert=True)

    def update_frame(self, name, frame):
        self.logger.info("Update frame: {0}".format(name))
        self.logger.debug("{0}".format(frame.head(3)))
        frame = frame.to_json(orient="split")
        self.__db.free.update({"_id": name}, {"_id": name, "data": frame}, upsert=True)
