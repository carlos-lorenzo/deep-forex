from typing import List, Dict
from collections.abc import Callable
from datetime import timedelta

from dataclasses import dataclass, field

from .timeframe import Timeframe, available_timeframes

@dataclass
class Query:
    episode_length: int
    trading_timeframe: str
    trading_column: str
    queries: List[Dict[str, Timeframe | int | Callable ]] = field(init=False, default_factory=list)
    
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
        return sum([query["window_size"] * 5 for query in self.queries]) # The 5 is a temporal hack, it will be inferred from data_processor function
    
    