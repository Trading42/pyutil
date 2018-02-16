from io import BytesIO

import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import attribute_mapped_collection

from pyutil.portfolio.portfolio import Portfolio

Base = declarative_base()

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Date, Float, LargeBinary
from sqlalchemy.orm import relationship


class Type(Base):
    __tablename__ = "symbolsapp_reference_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name =  Column(String(50), unique=True)
    fields = relationship("Field", back_populates = "type")


class Field(Base):
    __tablename__ = "symbolsapp_reference_field"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name =  Column(String(50), unique=True)
    type_id = Column(Integer, ForeignKey('symbolsapp_reference_type.id'))
    type = relationship("Type", back_populates="fields")
    data = relationship("SymbolReference", back_populates = "field")

    def __repr__(self):
        return "Field: {name}".format(name=self.name)

class SymbolReference(Base):
    __tablename__ = 'symbolsapp_reference_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey('symbolsapp_reference_field.id'))
    field = relationship("Field", back_populates="data")
    symbol_id = Column(Integer, ForeignKey("symbolsapp_symbol.id"))
    symbol = relationship("Symbol", back_populates="ref")
    content = Column(String(50))
    UniqueConstraint('symbol_id', 'field_id')

    def __repr__(self):
        return "Symbol: {symbol}\n{field}\nValue: {value}".format(symbol=self.symbol, field=self.field, value=self.content)


class SymbolGroup(Base):
    __tablename__ = "symbolsapp_group"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    symbols = relationship("Symbol", back_populates="group")

    def __repr__(self):
        return "Group: {name}".format(name=self.name)

class Symbol(Base):
    __tablename__ = "symbolsapp_symbol"
    id = Column(Integer, primary_key=True, autoincrement=True)
    bloomberg_symbol = Column(String(50), unique=True)
    group_id = Column(Integer, ForeignKey('symbolsapp_group.id'))
    group = relationship("SymbolGroup", back_populates="symbols")

    timeseries = relationship("Timeseries", collection_class=attribute_mapped_collection('name'), back_populates="symbol")
    ref = relationship("SymbolReference", collection_class=attribute_mapped_collection('field.name'), back_populates="symbol")

    @property
    def reference(self):
        return pd.Series({key: x.content for key,x in self.ref.items()})

    def __repr__(self):
        return "{name} in group {group}".format(name=self.bloomberg_symbol, group=self.group)

    def update_reference(self, field, value):
        if field.name not in self.ref.keys():
            self.ref[field.name] = SymbolReference(field=field, symbol=self, content=value)
        else:
            self.ref[field.name].content = value


class Timeseries(Base):
    __tablename__ = 'ts_name'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name =  Column(String(50))
    symbol_id = Column(Integer, ForeignKey('symbolsapp_symbol.id'))
    symbol = relationship("Symbol", back_populates="timeseries")
    data = relationship("TimeseriesData", collection_class=attribute_mapped_collection('date'), back_populates="ts")
    UniqueConstraint('symbol', 'name')

    @property
    def series(self):
        return pd.Series({pd.Timestamp(date): x.value for date, x in self.data.items()})

    def __repr__(self):
        return "{name} for {symbol}".format(name=self.name, symbol=self.symbol)

    @property
    def empty(self):
        return len(self.data) == 0

    @property
    def last_valid(self):
        if self.empty:
            return None
        else:
            return max(x for x in self.data.keys())

    def upsert(self, ts):
        for date, value in ts.items():
            if date in self.data.keys():
                # thes is some data
                self.data[date].value = value
            else:
                self.data[date] = TimeseriesData(date=date, value=value, ts_id=self.id)

            #upsert(TimeseriesData, get={"ts": self, "date": date}, set={"value": value})

class TimeseriesData(Base):
    __tablename__ = 'ts_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    value = Column(Float)
    ts_id = Column(Integer, ForeignKey('ts_name.id'))
    ts = relationship("Timeseries", back_populates="data")
    UniqueConstraint("date", "ts")


class PortfolioSQL(Base):

    __tablename__ = 'portfolio'
    name = Column(String, primary_key=True)
    weights = Column(LargeBinary)
    prices = Column(LargeBinary)
    #strategy = Column(Integer, ForeignKey("strategiesapp_strategy.id"), nullable=True)

    def __init__(self, portfolio, name, strategy=None):
        self.name = name
        if strategy:
            self.strategy = strategy
        # going through setter?
        self.weights = portfolio.weights.to_json(orient="split", date_format="iso").encode()
        # going through setter
        self.prices = portfolio.prices.to_json(orient="split", date_format="iso").encode()

    @staticmethod
    def read(x):
        json_str = BytesIO(x).read().decode()
        return pd.read_json(json_str, orient="split")

    @property
    def portfolio(self):
        return Portfolio(weights=self.weight, prices=self.price)

    @property
    def weight(self):
        return self.read(self.weights)

    @property
    def price(self):
        return self.read(self.prices)

    @price.setter
    def price(self, value):
        self.prices =  value.to_json(orient="split", date_format="iso").encode()

    @weight.setter
    def weight(self, value):
        self.weights =  value.to_json(orient="split", date_format="iso").encode()

    @property
    def last_valid(self):
        return self.portfolio.index[-1]

    @property
    def assets(self):
        return self.portfolio.assets

    @property
    def nav(self):
        return self.portfolio.nav

    def sector(self, map):
        # compile the symbolmap
        #mapping = {asset: Symbol(bloomberg_symbol=asset).group.name for asset in self.assets}
        return self.portfolio.sector_weights(symbolmap=map, total=False)

    def truncate(self, after=None, before=None):
        return self.portfolio.truncate(before=before, after=after)


class Frame(Base):
    __tablename__ = 'frame'
    name = Column(String, primary_key=True)
    data = Column(LargeBinary)
    index = Column(String)


    def __init__(self, frame, name):
        self.frame = frame
        self.name = name

    @property
    def frame(self):
        json_str = BytesIO(self.data).read().decode()
        return pd.read_json(json_str, orient="split").set_index(keys=self.index.split(","))

    @frame.setter
    def frame(self, value):
        self.index = ",".join(value.index.names)
        self.data = value.reset_index().to_json(orient="split", date_format="iso").encode()