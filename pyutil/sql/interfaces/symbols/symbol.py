import enum as _enum
import pandas as pd

import sqlalchemy as sq
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.types import Enum as _Enum

from pyutil.sql.interfaces.products import ProductInterface, Products


class SymbolType(_enum.Enum):
    alternatives = "Alternatives"
    fixed_income = "Fixed Income"
    currency = "Currency"
    equities = "Equities"


class Symbol(ProductInterface):
    __group = sq.Column("group", _Enum(SymbolType))
    internal = sq.Column(sq.String, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "symbol"}

    def __init__(self, name, group=None, internal=None):
        super().__init__(name)
        self.__group = group
        self.internal = internal

    @hybrid_property
    def group(self):
        return self.__group.name


class Symbols(Products):
    def __init__(self, symbols):
        super().__init__(symbols, cls=Symbol, attribute="name")

    @hybrid_property
    def internal(self):
        return {asset: asset.internal for asset in self.list}

    @hybrid_property
    def group(self):
        return {asset: asset.group for asset in self.list}

    @property
    def group_internal(self):
        # todo: fillna not working?
        return pd.DataFrame({"Group": pd.Series(self.group), "Internal": pd.Series(self.internal)})

