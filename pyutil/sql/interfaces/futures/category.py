from pyutil.sql.interfaces.products import ProductInterface


class FuturesCategory(ProductInterface):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
