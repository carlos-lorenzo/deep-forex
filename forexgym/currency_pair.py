from typing import List, Dict
from collections.abc import Callable

import pandas as pd

from .query import Query
from .timeframe import available_timeframes

class CurrencyPair:
    def __init__(self, ticker: str, timeframes: List[str], time_column: str = "Date", *args, **kwargs):
        self.ticker = ticker
        self.timeframes: Dict[str, pd.DataFrame] = {}
        self.time_column = time_column
        
        self._generate_timeframes(timeframes, time_column=time_column, drop_volume=True, *args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.ticker} - {self.timeframes.keys()}"
    
    def _load_tf(self, timeframe: str, time_column: str = "Time", *args, **kwargs) -> pd.DataFrame:
        if path := kwargs.get("path"):
            df = pd.read_csv(path)
        else:
            df = pd.read_csv(f"datasets/{self.ticker}/{timeframe}.csv")
        
        # TODO: Download if not found
        
        if kwargs.get("drop_volume", False):
            try:
                df = df.drop(["Volume"], axis=1)
            except KeyError:
                # Volume column not found
                # TODO: Add warning
                pass
        
        df[time_column] = pd.to_datetime(df[time_column], dayfirst=True, utc=True)
            
        return df
    
    def _generate_timeframes(self, timeframes: str, time_column: str, *args, **kwargs) -> None:
        for i, timeframe in enumerate(timeframes):
            if paths := kwargs.get("paths"):
                self.timeframes[timeframe] = self._load_tf(timeframe=timeframe, time_column=time_column, path=paths[i], *args, **kwargs)
            else:
                self.timeframes[timeframe] = self._load_tf(timeframe=timeframe, time_column=time_column, *args, **kwargs)
                
    
    def generate_dataset(self, query: Query) -> pd.DataFrame:
        #time_required = query.time_required
        #episode_length = query.episode_length
        trading_timeframe = query.trading_timeframe
        trading_column = query.trading_column
        
        trading_df = self.timeframes[trading_timeframe]
        
        
        episode_data = pd.DataFrame()
        episode_data["Date"] = trading_df["Date"]
        episode_data[f"Trading_{trading_column}"] = trading_df[trading_column] # TODO: Include OHLC
        
        
        
        
        for query_params in query.queries:
            timeframe = query_params["timeframe"]
            window_size = query_params["window_size"]
            current_tf = self.timeframes[timeframe.lable]
            data_processor: Callable[[pd.Series, int], pd.Series] = query_params.get("data_processor", self.default_processor)
            
            valid = current_tf[self.time_column].isin(trading_df[self.time_column])
            
            stacked = pd.concat([current_tf.drop([self.time_column], axis=1).add_suffix(f"_{i}").shift(i) for i in range(window_size)], axis=1)
            filtered: pd.DataFrame = stacked[valid].reset_index(drop=True).apply(lambda row: data_processor(row, window_size), axis=1)
            filtered = filtered.add_prefix(f"{timeframe.lable}_")
            
            episode_data = pd.concat([episode_data, filtered], axis=1)    
        
        
        return episode_data.dropna()
    
    def default_processor(self, row: pd.Series, window_size: int = 0, *args, **kwargs) -> pd.Series:
        return row
        
        