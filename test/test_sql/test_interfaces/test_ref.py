import pandas as pd
import pytest

from pyutil.mongo.mongo import create_collection
from test.test_sql.product import Product
import pandas.util.testing as pdt


@pytest.fixture()
def product():
    Product.__collection__ = create_collection()
    Product.__collection_reference__ = create_collection()
    product = Product(name="A")
    product["aaa"] = "A"
    product["bbb"] = "Z"
    return product


class TestReference(object):
    def test_ref_new_none(self, product):
        assert product["NoNoNo"] is None

    def test_ref_new(self, product):
        assert product["bbb"] == "Z"

    def test_ref_series(self, product):
        pdt.assert_series_equal(product.reference_series, pd.Series({"aaa": "A", "bbb": "Z"}))

    def test_ref_frame(self, product):
        f1 = Product._reference_frame(products=[product])
        f2 = pd.DataFrame(index=[product], columns=["aaa", "bbb"], data=[["A", "Z"]])
        f2.index.name = "product"
        pdt.assert_frame_equal(f1, f2)

    def test_name(self, product):
        assert product.name == "A"
