import pandas as pd
import pandas.util.testing as pdt

from mongoengine import *

from pyutil.mongo.engine.frame import Frame
from pyutil.mongo.engine.strategy import Strategy
from pyutil.mongo.engine.symbol import Symbol, Group
from test.config import mongo_client


#class Correlation(PandasDocument):
#    symbol1 = ReferenceField(Symbol)
#    symbol2 = ReferenceField(Symbol)


class TestEngine(object):
    def test_mock(self, mongo_client):
        # Create a new page and add tags
        group = Group(name="US Equity")
        group.save()

        symbol = Symbol(name='IBM US Equity', group=group)
        # you can add on the dictionary on the fly
        symbol.tags = ['mongodb', 'mongoengine']
        symbol.reference["XXX"] = "A"
        symbol.reference["YYY"] = "B"

        symbol.save()

        print(Symbol.reference_frame(products=[symbol], f=lambda x: x.name))
        #assert False

        assert Symbol.objects(tags='mongoengine').count() == 1
        assert symbol.group == group

    def test_collection(self, mongo_client):
        # Create a new page and add tags
        group = Group(name="US Equity")
        group.save()

        symbol = Symbol(name='Using MongoEngine 2', group=group)
        symbol.tags = ['mongodb', 'mongoengine']
        symbol.open = pd.Series(data=[1.1, 2.1, 3.1], name="test")
        symbol.save()

        #c = Correlation(name="Correlation", symbol1=symbol, symbol2=symbol)
        #c.data = PandasDocument.parse(pd.Series(data=[1, 2, 3], name="test"))
        #c.save()

        for s in Symbol.objects:
            pdt.assert_series_equal(s.open, pd.Series(data=[1.1, 2.1, 3.1], name="test"))
            try:
                x = s.px_last
            except AttributeError:
                x = None

            assert x is None


    def test_frame(self, mongo_client):
        frame = pd.DataFrame(data=[[1.1, 2.1], [3.1, 4.1]])

        f = Frame(name="Peter Maffay")
        f.data = frame
        f.save()

        for f in Frame.objects:
            pdt.assert_frame_equal(frame, f.data)

    def test_strategy(self, mongo_client):
        s = Strategy(name="mdt", type="mdt", active=True, source="AAA")


        print(s)