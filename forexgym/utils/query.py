from typing import List, Dict
from collections.abc import Callable
from datetime import timedelta, datetime

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .timeframe import Timeframe, available_timeframes

@dataclass
class Query:
    episode_length: int
    trading_timeframe: str
    trading_column: str
    lookback: int = field(default=100)
    queries: List[Dict[str, Timeframe | int | Callable]] = field(init=False, default_factory=list)
    
    
    def add_query(self, timeframe: Timeframe, window_size: int, data_processor: Callable = None) -> None:
        if timeframe not in available_timeframes:
            raise ValueError(f"Invalid timeframe: {timeframe} - Available timeframes: {list(available_timeframes.keys())}")
        query = {"timeframe": available_timeframes[timeframe], "window_size": window_size}
        if data_processor:
            query["data_processor"] = data_processor
        self.queries.append(query)
        
    
    @property
    def time_required(self) -> timedelta:
        max_delta = timedelta(0)
        for query in self.queries:
            max_delta = max(max_delta, query["timeframe"].value * query["window_size"])
        return max_delta
    
    @property
    def observation_size(self) -> int:
        # Create sample df
        ohlc = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close"])
        start = datetime(2000, 1, 1, 1)
        end = start + timedelta(hours=self.lookback-1)
        ohlc["Date"] = pd.date_range(start=start, end=end, freq=timedelta(hours=1))
        ohlc["Open"] = list(range(0, self.lookback))
        ohlc["High"] = list(range(0, self.lookback))
        ohlc["Low"] = list(range(0, self.lookback))
        ohlc["Close"] = list(range(0, self.lookback))
        ohlc["Volume"] = list(range(0, self.lookback))
        
        
        
        return sum([query["window_size"] * self._data_processor_dimension(ohlc, query) for query in self.queries])
    
    def _data_processor_dimension(self, df: pd.DataFrame, query: Dict[str, Timeframe | int | Callable]) -> int:
        try:
            return query["data_processor"](df).shape[1]
        except ValueError:
            raise ValueError(f"Data processor looks way into the past to infer output. Set lookback on init to requiered depth")