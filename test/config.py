import os

import pandas as pd
#import pytest

from pyutil.portfolio.portfolio import Portfolio
#from pyutil.sql.base import Base
from pyutil.testing.aux import resource_folder
#from pyutil.testing.database import database

pd.options.display.width = 300

# this is a function mapping name of a file to its path...
resource = resource_folder(folder=os.path.dirname(__file__))


def read(name, **kwargs):
    return pd.read_csv(resource(name), **kwargs)


def test_portfolio():
    return Portfolio(prices=read("price.csv", parse_dates=True, index_col=0),
                     weights=read("weight.csv", parse_dates=True, index_col=0))

#@pytest.fixture()
#def db():
#    # new db
#    return database(base=Base)
