from abc import ABC, abstractmethod

import pandas as pd

from .portfolio import Portfolio
from .event import Event


class Strategy(ABC):
    def __init__(self, lookback: int = 0) -> None:
        """Construct strategy with an initial amount of cash to allocate to the
        strategy"""
        self.lookback: int = lookback
        self.data: pd.DataFrame
        self._portfolio: Portfolio

    def order(self, symbol: str, price: float, qty: float) -> None:
        """Buy/Sell the stock updating portfolio with new position. If selling,
        use a negative qty"""
        self._portfolio.apply_order(symbol, price, qty)

    def on_start(self, data: pd.DataFrame, portfolio: Portfolio) -> None:
        """All data for the backtest"""
        self.data = data
        self._portfolio = portfolio

    @abstractmethod
    def on_event(self, event: Event) -> None:
        """Handle current price event"""


class BuyHoldStrategy(Strategy):
    """Buy and hold specified number of share of each symbol in provided data"""

    def __init__(self, num_shares: int = 1) -> None:
        super().__init__()  # Important, must call this
        self._num_shares = num_shares

    def on_event(self, event: Event) -> None:
        if event.number == 1:
            for sym, price in event.prices.items():
                self.order(sym, price, self._num_shares)


class AlternateBuySell(Strategy):
    def __init__(self, num_shares: int = 1) -> None:
        super().__init__()
        self._num_shares = num_shares
        self._buy_next = True

    def on_event(self, event: Event) -> None:
        if event.number == 1:
            for sym, price in event.prices.items():
                self.order(sym, price, self._num_shares)
            self._buy_next = False
        else:
            for sym, price in event.prices.items():
                if self._buy_next:
                    self.order(sym, price, self._num_shares)
                else:
                    self.order(sym, price, -self._num_shares)
            self._buy_next = not self._buy_next


class LowVolStrategy(Strategy):
    def __init__(self, num_shares: int = 1, lookback: int = 30) -> None:
        super().__init__(lookback=lookback)
        self._num_shares = num_shares
        self._bought = False

    def on_start(self, data: pd.DataFrame, portfolio: Portfolio) -> None:
        super().on_start(data, portfolio)
        self._compute_volatility()

    def _compute_volatility(self) -> None:
        returns = self.data.groupby(level=0)['close'].pct_change()
        self._volatilities = returns.groupby(level=0).std()

    def on_event(self, event: Event) -> None:
        if not self._bought:
            lowest_vol_symbol = self._volatilities.idxmin()
            price = event.prices[lowest_vol_symbol]
            self.order(lowest_vol_symbol, price, self._num_shares)
            self._bought = True


class Momentum(Strategy):
    def __init__(self, num_shares: int = 1) -> None:
        super().__init__(lookback=2)
        self._num_shares = num_shares
        self._positions: Dict[str, int] = {}

    def on_start(self, data: pd.DataFrame, portfolio: Portfolio) -> None:
        super().on_start(data, portfolio)
        for symbol in self.data.index.get_level_values(0).unique():
            self._positions[symbol] = 0

    def on_event(self, event: Event) -> None:
        if event.number <= 2:
            return

        for symbol, price in event.prices.items():
            returns = self.data.loc[symbol]['close'].pct_change().iloc[-2:]
            
            if all(returns > 0) and self._positions[symbol] > -self._num_shares:
                shares_to_short = min(self._num_shares, self._num_shares + self._positions[symbol])
                self.order(symbol, price, -shares_to_short)
                self._positions[symbol] -= shares_to_short
            
            elif all(returns < 0) and self._positions[symbol] < self._num_shares:
                shares_to_buy = min(self._num_shares, self._num_shares - self._positions[symbol])
                self.order(symbol, price, shares_to_buy)
                self._positions[symbol] += shares_to_buy