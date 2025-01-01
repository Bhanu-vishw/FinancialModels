from datetime import datetime, timedelta
from typing import Iterable
from unittest import mock

import pandas as pd
import numpy as np

import backtestlib as bt


def make_dummy_history(
    start: datetime, end: datetime, interval: bt.Interval, symbols: Iterable[str]
) -> pd.DataFrame:
    """Helper function to make dummy data according to contract"""
    index = pd.MultiIndex.from_product(
        [symbols, pd.date_range(start, end, freq=bt.interval_to_pandas_freq(interval))],
        names=["symbol", "date"],
    )
    df = pd.DataFrame(
        index=index,
        data={"close": np.arange(len(index)) + 100},
    )
    return df


def test_run():
    """Test data flows through backtest.run() method for daily interval"""
    symbols = ("ABC", "DEF")
    start = datetime(2024, 10, 9)
    end = datetime(2024, 10, 11)
    interval = bt.Interval.DAY

    strategy = mock.create_autospec(bt.Strategy)
    strategy.lookback = 10
    provider = mock.create_autospec(bt.DataProvider)
    provider.query.side_effect = lambda *args: make_dummy_history(*args)

    # 10 business days prior to 2024/10/9
    expected_dp_start = datetime(2024, 9, 25)
    backtest = bt.Backtest(
        symbols=symbols,
        data_provider=provider,
        strategy=strategy,
        interval=interval,
    )
    backtest.run(start=start, end=end)

    # Ensure expected symbols get forwarded to provider. We need to go start - lookback period
    provider.query.assert_called_once_with(expected_dp_start, end, interval, symbols)
    # on_start should only be called at the beginning of the backtest
    strategy.on_start.assert_called_once()
    # on_event should be called for each period in start...end but not include lookback period
    assert strategy.on_event.call_count == 3
    # check each call matches expected dispatched event
    strategy.on_event.assert_called_with(bt.Event(3, end, {"ABC": 112, "DEF": 125}))
    calls = [
        mock.call(bt.Event(1, start, {"ABC": 110, "DEF": 123})),
        mock.call(bt.Event(2, start + timedelta(days=1), {"ABC": 111, "DEF": 124})),
        mock.call(bt.Event(3, start + timedelta(days=2), {"ABC": 112, "DEF": 125})),
    ]
    assert strategy.on_event.call_args_list == calls
