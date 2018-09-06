

class SimpleTestData(object):

    def __init__(self, _data=""):
        self._data = _data

    def __repr__(self):
        return self._data


    @classmethod
    def wallet(cls, wallet="0005-2070-2000-0006-0200"):
        return cls(_data=wallet)

    @classmethod
    def test_id(cls, t_id="9999"):
        return cls(_data=t_id)

    @classmethod
    def condition(cls, con="tryam"):
        return cls(_data=con)