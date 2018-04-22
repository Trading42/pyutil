import pandas as _pd
import sqlalchemy as sq
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from pyutil.sql.base import Base
from pyutil.sql.immutable import ReadDict
from pyutil.sql.model.ref import ReferenceData, Field
from pyutil.sql.model.ts import Timeseries


class ProductInterface(Base):
    __tablename__ = "productinterface"
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    discriminator = sq.Column(sq.String)

    __mapper_args__ = {"polymorphic_on": discriminator}

    _refdata = relationship(ReferenceData, collection_class=attribute_mapped_collection("field"),
                            cascade="all, delete-orphan", backref="product")

    _timeseries = relationship(Timeseries, collection_class=attribute_mapped_collection('key'),
                               cascade="all, delete-orphan", backref="product", foreign_keys=[Timeseries.product_id])

    @property
    def reference(self):
        return ReadDict(seq={field.name: x.value for field, x in self._refdata.items()}, default=None)

    @property
    def timeseries(self):
        return ReadDict(seq={ts: x.series for ts, x in self._timeseries.items()}, default=_pd.Series({}))

    def upsert_ts(self, name, data=None, secondary=None):
        """ upsert a timeseries, get Timeseries object """

        def key(name, secondary=None):
            if secondary:
                return name, secondary
            else:
                return name
        k = key(name, secondary)

        if k not in self._timeseries.keys():
            self._timeseries[k] = Timeseries(name=name, product=self, secondary=secondary)

        return self._timeseries[k].upsert(data)

    def upsert_ref(self, field, value):
        assert isinstance(field, Field)

        if field not in self._refdata.keys():
            r = ReferenceData(field=field, product=self, content=value)
            self._refdata[field] = r
        else:
            self._refdata[field].content = value

    def frame(self, name):
        return _pd.DataFrame({x.secondary: x.series for x in self._timeseries.values() if x.name == name and x.secondary})