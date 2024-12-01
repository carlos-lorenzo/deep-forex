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
        
        
        self._generate_timeframes(timeframes, time_column=time_column, drop_volume=kwargs.get("drop_volume", False), *args, **kwargs)
    
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
                

    
    def generate_dataset(self, query: Query,  *args, **kwargs) -> pd.DataFrame:
        
        trading_timeframe_lable = query.trading_timeframe
        trading_timeframe = available_timeframes[trading_timeframe_lable]
        trading_column = query.trading_column
        
        trading_df = self.timeframes[trading_timeframe_lable]
        
        
        episode_data = pd.DataFrame()
        episode_data[self.time_column] = trading_df[self.time_column]
        episode_data["Trading_Price"] = trading_df[trading_column] # TODO: Include OHLC
        
        
        
        for query_params in tqdm(query.queries):
            query_timeframe: Timeframe = query_params["timeframe"]
            window_size: int = query_params["window_size"]
            data_processor: Callable[[pd.DataFrame], pd.DataFrame] = query_params.get("data_processor", default_processor)
            
            # Selects the query dataframe
            query_df = self.timeframes[query_timeframe.lable]
            
            # Extracts features from the query dataframe
            processed_df = data_processor(query_df)
            
            # Creates a dataframe in which all rows contain all the features
            stacked = pd.concat([processed_df.add_suffix(f"_{shift}").shift(shift) for shift in range(window_size)], axis=1)
            
            # Smaller or equal than the trading TF
            if trading_timeframe >= query_timeframe:
                
                # Uses the existing dates in the trading dataframe to be included in the final datasets since all the other rows are irrelevant and will be discarded
                valid = query_df[self.time_column].isin(trading_df[self.time_column])
                
                # Selects the relevant rows (rows which share dates), adds a prefix and adds them to the final dataset
                filtered: pd.DataFrame = stacked[valid].reset_index(drop=True).add_prefix(f"{query_timeframe.lable}_")
                episode_data = pd.concat([episode_data, filtered], axis=1)
            
            # Greater TF than the trading TF 
            else:
                # Returns a pd.Series in which all dates of the trading dataframe have been rounded down to match that of the query (e.g. 12:00 -> 12:00, 12:15 -> 12:00, 12:30 -> 12:00, 12:45 -> 12:00)
                trading_dates = trading_df[self.time_column].copy().dt.floor(query_timeframe.value)
                
                # Includes the Date column back into the feature dataframe to be compared (the user probably has removed Date column from features)
                stacked[self.time_column] = query_df[self.time_column]
                
                # Given the trading dates (a series with Query Tf/Trading Tf n repeated rows 1H/15m = 4 repeated rows)
                # For each row (date) in trading dates the corresponding row (date) in the stacked dataframe is merged with the corresponding row (date) in the stacked dataframe such that the two rows share the same date
                # It therefore yields a dataframe consisting of merged rows with the same date so that for all divisiones in the trading TF it has data from the higher TFs
                # It is shifted n times to avoid lookahead bias
                # Ik its a bit confusing but it works
                
                
                filtered = pd.merge(trading_dates, stacked, on=self.time_column, how='outer').drop([self.time_column], axis=1).add_prefix(f"{query_timeframe.lable}_").shift(int(query_timeframe.value/trading_timeframe.value))
                
                # Filtered TF added horizontaly into the final dataset
                episode_data = pd.concat([episode_data, filtered], axis=1)
        
    
        episode_data = episode_data.dropna().reset_index(drop=True)
        
        if not kwargs.get("no_save", False):
            episode_data.to_csv(f"datasets/training/{self.ticker}.csv", index=False)
        
        print(f"Generated {self.ticker} dataset.")  
        
        return episode_data
    
    
    
    
        
        