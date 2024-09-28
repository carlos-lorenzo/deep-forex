from typing import List, Dict
from collections.abc import Callable
from datetime import timedelta

from dataclasses import dataclass, field

from .timeframe import Timeframe, available_timeframes

@dataclass
class Query:
    episode_length: int
    trading_timeframe: str
    queries: List[Dict[str, Timeframe | int | Callable ]] = field(init=False, default_factory=list)
    
    def add_query(self, timeframe: Timeframe, window_size: int, data_processor: Callable = None) -> None:
        if timeframe not in available_timeframes:
            raise ValueError(f"Invalid timeframe: {timeframe} - Available timeframes: {list(available_timeframes.keys())}")
        
        self.queries.append({"timeframe": available_timeframes[timeframe], "window_size": window_size, "data_processor": data_processor})
        
    
    @property
    def time_required(self) -> timedelta:
        max_delta = timedelta(0)
        for query in self.queries:
            max_delta = max(max_delta, query["timeframe"].value * query["window_size"])
        return max_delta
    
    