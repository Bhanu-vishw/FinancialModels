from datetime import datetime
from unittest import mock

import pandas as pd

import backtestlib as bt


class DummyStrategy(bt.Strategy):
    """Testing class for base methods since Strategy is an ABC"""

    def __init__(self, lookback: int = 0) -> None:
        super().__init__(lookback)

    def on_event(self, event: bt.Event) -> None:
        pass


def test_strategy_order_updates_portfolio():
    strategy = DummyStrategy()
    portfolio = mock.create_autospec(bt.Portfolio)
    strategy.on_start(pd.DataFrame(), portfolio)
    symbol, price, qty = "ABC", 123, 5
    prices = {symbol: price}

    strategy.on_event(bt.Event(1, datetime(2024, 10, 1), prices))
    strategy.order(symbol, price, qty)

    portfolio.apply_order.assert_called_with(symbol, price, qty)
