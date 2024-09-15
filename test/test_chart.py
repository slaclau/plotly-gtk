from datetime import datetime, timedelta
from test import get_random_strings

import numpy as np

import pytest
from plotly_gtk.chart import PlotlyGtk

_50categories = get_random_strings(50)
_1000categories = get_random_strings(1000)

_dates = np.arange(datetime(1900, 1, 1), datetime(2000, 1, 1), timedelta(days=1))
_50dates = np.random.choice(_dates, [50])
_50dates_str = _50dates.astype(str)
_1000dates = np.random.choice(_dates, [1000])
_10000dates = np.random.choice(_dates, [10000])


_50numbers = np.random.random([50])
_50numbers_list = list(_50numbers)
_1000numbers = np.random.random([1000])
_10000numbers = np.random.random([10000])
_25000numbers = np.random.random([25000])

_multicategory_example = [["a", "b"], ["c", "d", "e"]]

datasets = {
    "linear": {
        "50": _50numbers,
        "50 list": _50numbers_list,
        "1000": _1000numbers,
        "10000": _10000numbers,
        "25000": _25000numbers,
        "1000+1000 categories": np.concatenate(
            (_50categories, _1000numbers), dtype=object
        ),
    },
    "date": {
        "50": _50dates,
        "50 strings": _50dates_str,
        "1000": _1000dates,
        "10000": _10000dates,
        "1000+50 numbers": np.concatenate((_50numbers, _1000dates), dtype=object),
        "1000+50 categories": np.concatenate((_50categories, _1000dates), dtype=object),
    },
    "category": {
        "50": _50categories,
        "1000": _1000categories,
        "1000+50 numbers": np.concatenate((_50numbers, _1000categories), dtype=object),
        "1000+50 dates": np.concatenate((_50dates, _1000categories), dtype=object),
    },
    "multicategory": {"simple": _multicategory_example},
}


class TestPlotlyGtk:
    @pytest.mark.parametrize("data_type", datasets.keys())
    def test__detect_axis_type(self, subtests, data_type):
        for name, dataset in datasets[data_type].items():
            with subtests.test(msg=f"{data_type}-{name}"):
                assert PlotlyGtk._detect_axis_type(dataset) == data_type
