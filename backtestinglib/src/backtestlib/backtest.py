from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Iterable, Optional

import pandas as pd

from .data import DataProvider, Interval
from .event import Event
from .portfolio import Portfolio
from .strategy import Strategy


class Backtest:
    def __init__(
        self,
        symbols: Iterable[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = datetime.now(),
        strategy: Optional[Strategy] = None,
        interval: Optional[Interval] = Interval.DAY,
        data_provider: Optional[DataProvider] = None,
        cash: float = 1000,
    ) -> None:
        """_summary_

        Args:
            symbols (Iterable[str], optional): symbols to use
            start (Optional[datetime], optional): start date
            end (Optional[datetime], optional): end date
            strategy (Optional[Strategy], optional): strategy implementation
            interval (Optional[Interval], optional): time interval
            data_provider (Optional[DataProvider], optional): data provider implementation
            cash (float, optional): starting cash
        """
        self._symbols = symbols
        self._start = start
        self._end = end
        self._strategy = strategy
        self._interval = interval
        self._data_provider = data_provider
        self._cash = float(cash)
        self._portfolio = Portfolio(cash)

    def reset(self, cash: Optional[float] = None) -> None:
        """Resets portfolio with initial amount if cash"""
        self._cash = float(cash or self._cash)
        self._portfolio = Portfolio(self._cash)

    def value(self) -> None:
        """Current portfolio value"""
        return self._portfolio.value()

    def run(
        self,
        symbols: Iterable[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        strategy: Optional[Strategy] = None,
        interval: Optional[Interval] = None,
        data_provider: Optional[DataProvider] = None,
    ) -> None:
        """Run backtest, overriding any constructor arguments if desired"""
        self._symbols = symbols or self._symbols
        self._start = start or self._start
        self._end = end or self._end
        self._strategy = strategy or self._strategy
        self._interval = interval or self._interval
        self._data_provider = data_provider or self._data_provider

        if self._start > self._end:
            raise ValueError(
                f"Start date is after end date, start={self._start}, end={self._end}"
            )

        lookback_periods = self._strategy.lookback
        if interval == Interval.DAY:
            delta = relativedelta(months=lookback_periods)
        else:
            delta = pd.offsets.BusinessDay(n=lookback_periods)
        data = self._data_provider.query(
            self._start - delta, self._end, self._interval, self._symbols
        )
        self._strategy.on_start(data, self._portfolio)
        i: int
        dt: pd.Timestamp
        row: pd.DataFrame

        # Enumerate only over data since start date
        for i, (dt, row) in enumerate(
            data.loc[slice(None), slice(self._start, self._end), :].groupby(level=1)
        ):
            prices_by_sym = row.droplevel(1)["close"].to_dict()
            event = Event(i + 1, dt.to_pydatetime(), prices_by_sym)
            self._portfolio.on_event(event)
            self._strategy.on_event(event)
