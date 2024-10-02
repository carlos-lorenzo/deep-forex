import os
from typing import List, Dict
from collections.abc import Callable

from tqdm import tqdm

import pandas as pd

from .query import Query
from .timeframe import Timeframe, available_timeframes
from .data_processors import default_processor

class CurrencyPair:
    def __init__(self, ticker: str, timeframes: List[str], time_column: str = "Date", generate_data: bool = True, *args, **kwargs):
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
        
        #df[time_column] = pd.to_datetime(df[time_column], dayfirst=True)
        
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
                
    
    def generate_dataset(self, query: Query, *args, **kwargs) -> pd.DataFrame:
        trading_timeframe = query.trading_timeframe
        trading_column = query.trading_column
        
        trading_df = self.timeframes[trading_timeframe]
        
        
        episode_data = pd.DataFrame()
        episode_data[self.time_column] = trading_df[self.time_column]
        episode_data["Trading_Price"] = trading_df[trading_column] # TODO: Include OHLC
        
        
        
        print(f"Genrating {self.ticker} dataset...")
        for query_params in tqdm(query.queries):
            query_timeframe: Timeframe = query_params["timeframe"]
            window_size: int = query_params["window_size"]
            data_processor: Callable[[pd.DataFrame], pd.DataFrame] = query_params.get("data_processor", default_processor)
            
            
            query_df = self.timeframes[query_timeframe.lable]
            
            processed_df = data_processor(query_df)
            
            stacked = pd.concat([processed_df.add_suffix(f"_{shift}").shift(shift) for shift in range(window_size)], axis=1)
            
            if available_timeframes[trading_timeframe] >= query_timeframe:
                
                valid = query_df[self.time_column].isin(trading_df[self.time_column])
                filtered: pd.DataFrame = stacked[valid].reset_index(drop=True).add_prefix(f"{query_timeframe.lable}_")
                
                episode_data = pd.concat([episode_data, filtered], axis=1)
                
            else:
                trading_dates = trading_df[self.time_column].copy().dt.floor(query_timeframe.value)
                stacked[self.time_column] = query_df[self.time_column]
                filtered = pd.merge(trading_dates, stacked, on=self.time_column, how='outer').drop([self.time_column], axis=1).add_prefix(f"{query_timeframe.lable}_")
                
                episode_data = pd.concat([episode_data, filtered], axis=1)
        
        if not os.path.isdir("datasets/training"):
            os.mkdir("datasets/training")
        
        episode_data = episode_data.dropna().reset_index(drop=True)
        
        episode_data.to_csv(f"datasets/training/{self.ticker}.csv", index=False)
        
        print(f"Generated {self.ticker} dataset.")
        
        return episode_data
    
    
        
        