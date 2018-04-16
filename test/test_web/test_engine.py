import json
from unittest import TestCase

from pyutil.web.engine import month, performance
from test.config import series2arrays, read_frame


class Request(object):
    def __init__(self, data):
        self.__data = data.encode('utf-8')

    @property
    def data(self):
        return self.__data


class TestDatabase(TestCase):
    @classmethod
    def setUpClass(cls):
        ts = read_frame("price.csv")["A"].dropna()
        cls.request = Request(data=json.dumps(series2arrays(ts)))

    def test_month(self):
        x = month(self.request)
        self.assertListEqual(x["columns"], ['Year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'STDev', 'YTD'])
        self.assertDictEqual(x["data"][0], {'Apr': '1.43%', 'Aug': '', 'Dec': '', 'Feb': '-5.50%', 'Jan': '8.35%', 'Jul': '', 'Jun': '', 'Mar': '-2.43%', 'May': '', 'Year': '2015', 'Nov': '', 'Oct': '', 'STDev': '20.69%', 'Sep': '', 'YTD': '1.33%'})

    def test_performance(self):
        x = performance(self.request)
        self.assertListEqual(x["data"], [{'name': 'Return', 'value': '-28.27'}, {'name': '# Events', 'value': '601'},
                                         {'name': '# Events per year', 'value': '261'},
                                         {'name': 'Annua Return', 'value': '-14.43'},
                                         {'name': 'Annua Volatility', 'value': '18.03'},
                                         {'name': 'Annua Sharpe Ratio (r_f = 0)', 'value': '-0.80'},
                                         {'name': 'Max Drawdown', 'value': '32.61'},
                                         {'name': 'Max % return', 'value': '4.07'},
                                         {'name': 'Min % return', 'value': '-9.11'}, {'name': 'MTD', 'value': '1.43'},
                                         {'name': 'YTD', 'value': '1.33'}, {'name': 'Current Nav', 'value': '1200.59'},
                                         {'name': 'Max Nav', 'value': '1692.70'},
                                         {'name': 'Current Drawdown', 'value': '29.07'},
                                         {'name': 'Calmar Ratio (3Y)', 'value': '-0.44'},
                                         {'name': '# Positive Events', 'value': '285'},
                                         {'name': '# Negative Events', 'value': '316'},
                                         {'name': 'Value at Risk (alpha = 95)', 'value': '1.91'},
                                         {'name': 'Conditional Value at Risk (alpha = 95)', 'value': '2.76'},
                                         {'name': 'First_at', 'value': '2013-01-01'},
                                         {'name': 'Last_at', 'value': '2015-04-22'}])


