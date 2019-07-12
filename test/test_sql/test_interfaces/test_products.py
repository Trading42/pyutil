import pandas as pd
import pandas.util.testing as pdt
import pytest

from pyutil.mongo.mongo import create_collection
from pyutil.sql.interfaces.products import ProductInterface
from test.test_sql.product import Product


@pytest.fixture()
def ts1():
    return pd.Series(data=[100, 200], index=[0, 1])


@pytest.fixture()
def ts2():
    return pd.Series(data=[300, 300], index=[1, 2])


@pytest.fixture()
def ts3():
    return pd.Series(data=[100, 300, 300], index=[0, 1, 2])


# point to a new mongo collection...
ProductInterface.__collection__ = create_collection()
ProductInterface.__collection_reference__ = create_collection()


class TestProductInterface(object):
    def test_name(self):
        assert Product(name="A").name == "A"

        # you can not change the name of a product!
        with pytest.raises(AttributeError):
            Product(name="A").name = "AA"

        assert Product.__collection__
        assert Product.__collection_reference__

    def test_timeseries(self, ts1):
        product = Product(name="A")
        product.write(data=ts1, key="y")
        pdt.assert_series_equal(ts1, product.read(key="y"))

    def test_merge(self, ts1, ts2):
        product = Product(name="A")
        product.write(data=ts1, key="x")
        product.write(data=ts2, key="x")
        pdt.assert_series_equal(product.read(key="x"), ts2)
        frame = Product._pandas_frame(products=[product], key="x")
        pdt.assert_series_equal(frame["A"], ts2, check_names=False)

    def test_lt(self):
        p1 = Product(name="A")
        p2 = Product(name="B")
        assert p1 < p2

    def test_meta(self):
        p1 = Product(name="A")
        p2 = Product(name="B")
        p1["xxx"] = 1
        p1["yyy"] = 2
        p2["zzz"] = 3

        frame = Product._reference_frame(products=[p1, p2]).transpose()
        assert frame[p1]["yyy"] == 2
        assert frame[p2]["zzz"] == 3

