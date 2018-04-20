from pyutil.sql.base import Base
from sqlalchemy.types import Enum
import sqlalchemy as sq
import enum as enum


class FieldType(enum.Enum):
    dynamic = "dynamic"
    static = "static"
    other = "other"


class DataType(enum.Enum):
    string = ("string", lambda x: x)
    integer = ("integer", lambda x: int(x))
    float = ("float", lambda x: float(x))
    date = ("date", lambda x: pd.to_datetime(int(x)*1e6).date())
    datetime = ("datetime", lambda x: pd.to_datetime(int(x)*1e6))
    percentage = ("percentage", lambda x: float(x))

    def __init__(self, value, fct):
        self.__v = value
        self.__fct = fct

    @property
    def value(self):
        # this is a bit of a hack, we are overriding the value attribute of the enum...
        return self.__v

    def __call__(self, *args):
        return self.__fct(*args)


class Field(Base):
    __tablename__ = "reference_field"
    _id = sq.Column("id", sq.Integer, primary_key=True, autoincrement=True)
    name = sq.Column(sq.String(50), unique=True)
    type = sq.Column(Enum(FieldType))
    result = sq.Column(Enum(DataType), nullable=False)

    def __repr__(self):
        return "{name}".format(name=self.name)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash(str(self.name))


class ReferenceData(Base):
    __tablename__ = "reference_data"
    _field_id = sq.Column("field_id", sq.Integer, sq.ForeignKey(Field._id), primary_key=True)
    content = sq.Column(sq.String(200), nullable=False)
    product_id = sq.Column(sq.Integer, sq.ForeignKey("productinterface.id"), primary_key=True)

    def __repr__(self):
        return "{field} for {x}: {value}".format(field=self.field.name, value=self.content, x=self.product)

    def __init__(self, field=None, product=None, content=None):
        self.content = content
        self.field = field
        self.product = product

    @property
    def value(self):
        return self.field.result(self.content)

    @value.setter
    def value(self, x):
        self.content = str(x)
