from datetime import datetime

import pandas as pd
import pytest

import backtestlib as bt


def test_interval_year_frac():
    assert bt.Interval.to_year_frac(bt.Interval.DAY) == 1 / 252
    assert bt.Interval.to_year_frac(bt.Interval.MONTH) == 1 / 12


def test_interval_to_pandas_freq():
    assert bt.interval_to_pandas_freq(bt.Interval.DAY) == "B"
    assert bt.interval_to_pandas_freq(bt.Interval.MONTH) == "MS"


@pytest.mark.parametrize(
    "start,end,interval",
    [
        (datetime(2024, 1, 1), datetime(2024, 1, 18), bt.Interval.DAY),
        (datetime(2022, 1, 1), datetime(2025, 1, 1), bt.Interval.MONTH),
    ],
)
def test_constant_return_data_provider(
    start: datetime, end: datetime, interval: bt.Interval
):
    symbols = ("ABC", "DEF", "GHI")
    default_s0 = 125
    default_ret = 0.5
    s0_map = {"ABC": 500, "GHI": 1000}
    ret_map = {"ABC": 0.2, "GHI": 0.8}
    provider = bt.ConstantReturnDataProvider(
        default_s0=default_s0,
        default_return=default_ret,
        s0_map=s0_map,
        return_map=ret_map,
    )
    data = provider.query(
        start=start,
        end=end,
        interval=interval,
        symbols=symbols,
    )

    # structure
    assert tuple(data.index.levels[0]) == symbols
    date_range: pd.DatetimeIndex = data.index.levels[1]
    assert date_range[0].to_pydatetime() == start
    assert date_range[-1].to_pydatetime() == end

    # data
    dt = bt.Interval.to_year_frac(interval)
    s0_abc, ret_abc = s0_map["ABC"], ret_map["ABC"]
    assert data.loc["ABC", start]["close"] == s0_abc
    last_price = data.loc["ABC", end]["close"]
    time_to_last_price = dt * (len(date_range) - 1)
    assert pytest.approx(last_price) == s0_abc * (1 + ret_abc) ** time_to_last_price
