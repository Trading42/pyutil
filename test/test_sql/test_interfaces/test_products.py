from unittest import TestCase

import pandas as pd
import pandas.util.testing as pdt

from pyutil.sql.interfaces.ref import Field, FieldType, DataType
from pyutil.timeseries.merge import merge
from test.test_sql.product import Product

t0 = pd.Timestamp("2010-05-14")
t1 = pd.Timestamp("2010-05-15")


class TestProductInterface(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p1 = Product(name="A")
        cls.p2 = Product(name="B")

        cls.f1 = Field(name="x", type=FieldType.dynamic, result=DataType.integer)
        cls.f2 = Field(name="y", type=FieldType.dynamic, result=DataType.string)

    def test_name(self):
        self.assertEqual(self.p1.name, "A")

    def test_name_invariant(self):
        # you can not change the name of a product!
        with self.assertRaises(AttributeError):
            self.p1.name = "AA"

    def test_reference(self):
        self.p1.reference[self.f1] = "100"
        self.assertEqual(self.p1.reference[self.f1], 100)

        self.p1.reference[self.f1] = "120"
        self.assertEqual(self.p1.reference[self.f1], 120)
        self.assertFalse(self.f2 in self.p1.reference.keys())

        with self.assertRaises(KeyError):
            self.p1.reference[self.f2]

        self.p1.reference[self.f2] = "10"
        self.p1.reference[self.f2] = "11"

        self.assertTrue(self.f1 < self.f2)

        self.assertTrue(self.f2 in self.p1.reference.keys())
        self.assertDictEqual({self.f1: 120, self.f2: "11"}, dict(self.p1.reference))

        frame = pd.DataFrame(index=[self.p1.name], columns=["x", "y"], data=[[120, "11"]])
        frame.index.name = "Product"

    def test_with_unknown_fields(self):
        f = Field(name="z", type=FieldType.dynamic, result=DataType.integer)
        self.assertEqual(self.p1.get_reference(field=f, default=5), 5)
        self.assertIsNone(self.p1.get_reference(field=f))
        self.assertEqual(self.p1.get_reference(field="z", default=5), 5)

    def test_discriminator(self):
        self.assertEqual(self.p1.discriminator, "Test-Product")

    def test_hash(self):
        x = {self.p1, self.p2}
        assert self.p1 in x

    def test_timeseries(self):
        a = merge(pd.Series(index=[0, 1], data=[4, 5]))
        b = pd.Series(index=[1, 3], data=[10, 12])
        c = merge(old=a, new=b)

        pdt.assert_series_equal(pd.Series(index=[0, 1, 3], data=[4, 10, 12]), c)
