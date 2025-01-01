from abc import ABC, abstractmethod
from datetime import datetime
from enum import IntEnum
from typing import Iterable, Optional, Self

import pandas as pd
import numpy as np
import yfinance as yf


class Interval(IntEnum):
    DAY = 1
    MONTH = 2

    @staticmethod
    def to_year_frac(interval: "Interval") -> float:
        match interval:
            case Interval.DAY:
                return 1.0 / 252.0
            case Interval.MONTH:
                return 1.0 / 12.0
            case _:
                raise ValueError(f"Unexpected interval: {interval}")


def interval_to_pandas_freq(interval: "Interval") -> str:
    match interval:
        case Interval.DAY:
            return "B"
        case Interval.MONTH:
            return "MS"
        case _:
            raise ValueError(f"Unexpected interval: {interval}")


class DataProvider:
    """Daily return provider"""

    @abstractmethod
    def query(
        self,
        start: datetime,
        end: datetime,
        interval: Interval,
        symbols: Iterable[str],
    ) -> pd.DataFrame:
        pass


class ConstantReturnDataProvider(DataProvider):
    """Generate prices with constant returns from start date to end date"""

    def __init__(
        self,
        default_s0: float = 100,
        default_return: float = 0.25,
        s0_map: Optional[dict[str, float]] = None,
        return_map: Optional[dict[str, float]] = None,
    ) -> None:
        """
        Args:
            default_s0 (float): default initial price
            default_return (float): default annualized return
            s0_map (Optional[dict[str, float]], optional): map of symbols to initial prices
            return_map (Optional[dict[str, float]], optional): map of symbols to returns
        """
        self.default_s0 = default_s0
        self.default_return = default_return
        self.s0_map = s0_map or {}
        self.return_map = return_map or {}

    def query(
        self,
        start: datetime,
        end: datetime,
        interval: Interval,
        symbols: Iterable[str],
    ) -> pd.DataFrame:
        date_range = pd.date_range(
            start=start, end=end, freq=interval_to_pandas_freq(interval)
        )
        index = pd.MultiIndex.from_product(
            [symbols, date_range], names=["symbol", "datetime"]
        )
        df = pd.DataFrame(index=index)
        dts = np.arange(len(date_range)) * Interval.to_year_frac(interval)
        for symbol in symbols:
            s0 = self.s0_map.get(symbol, self.default_s0)
            r = self.return_map.get(symbol, self.default_return)
            df.loc[symbol, "close"] = s0 * (1 + r) ** dts
        return df


class YahooDataProvider(DataProvider):
    """Provide data from Yahoo! Finance"""

    # Your implementation
    def query(
        self,
        start: datetime,
        end: datetime,
        interval: Interval,
        symbols: Iterable[str],
    ) -> pd.DataFrame:
        # Convert interval to yfinance format
        yf_interval = self._convert_interval(interval)

        # Fetch data for all symbols
        data = yf.download(
            tickers=list(symbols),
            start=start,
            end=end,
            interval=yf_interval,
            group_by='ticker',
            auto_adjust=True,
            progress=False
        )

        # Reshape the data to match the expected format
        df = self._reshape_data(data, symbols, start, end, interval)

        return df

    def _convert_interval(self, interval: Interval) -> str:
        if interval == Interval.DAY:
            return "1d"
        elif interval == Interval.MONTH:
            return "1mo"
        else:
            raise ValueError(f"Unsupported interval: {interval}")

    def _reshape_data(self, data: pd.DataFrame, symbols: Iterable[str], start: datetime, end: datetime, interval: Interval) -> pd.DataFrame:
        # Create a complete date range
        date_range = pd.date_range(start=start, end=end, freq=interval_to_pandas_freq(interval))
        
        reshaped_data = []

        for symbol in symbols:
            if symbol in data.columns.levels[0]:
                symbol_data = data[symbol]['Close'].reindex(date_range)
                symbol_data = symbol_data.reset_index()
                symbol_data['symbol'] = symbol
                reshaped_data.append(symbol_data)
            else:
                symbol_data = pd.DataFrame({
                    'datetime': date_range,
                    'Close': np.nan,
                    'symbol': symbol
                })
                reshaped_data.append(symbol_data)

        result = pd.concat(reshaped_data, ignore_index=True)
        result = result.rename(columns={'index': 'datetime', 'Close': 'close'})
        result = result.set_index(['symbol', 'datetime']).sort_index()
        return result
