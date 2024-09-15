import pytest
from plotly_gtk.utils import get_base_fig, update_dict
from plotly_gtk.utils.ticks import Ticks

base_fig = get_base_fig()
base_fig = update_dict(base_fig, base_fig["layout"]["template"])


class TestBasic:
    @pytest.fixture()
    def ticks_object(self):
        update = {"xaxis": {"_range": [0, 100], "_type": "linear", "nticks": 0}}
        fig = update_dict(base_fig["layout"], update)
        rtn = Ticks(fig, "xaxis", 100)
        rtn.prepare()
        return rtn

    def test_tick_first(self, ticks_object):
        assert ticks_object.tick_first() == 0

    def test_tick_increment(self):
        assert False

    def test_calculate(self):

        assert False

    def test_prepare(self):

        assert False

    def test_round_up(self):

        assert False

    def test_round_dtick(self):

        assert False

    def test_auto_ticks(self):

        assert False

    def test_array_ticks(self):

        assert False
