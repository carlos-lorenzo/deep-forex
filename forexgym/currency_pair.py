from typing import List, Dict

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
                
    
    def query_episode(self, query: Query) -> pd.DataFrame:
        time_required = query.time_required
        episode_length = query.episode_length
        trading_timeframe = query.trading_timeframe
        trading_df = self.timeframes[trading_timeframe]
        
        
        first_time = trading_df.iloc[0][self.time_column] + time_required
        last_time = trading_df.iloc[-1][self.time_column] - available_timeframes[trading_timeframe].value * episode_length
        
        start_row = trading_df[(trading_df[self.time_column] >= first_time) & (trading_df[self.time_column] <= last_time)].sample(1).index[0]
        end_row = start_row + episode_length
        
        selected_start_time = trading_df.iloc[start_row][self.time_column]
        selected_end_time = trading_df.iloc[end_row][self.time_column]
        
        episode_data = pd.DataFrame()
        episode_data["Date"] = trading_df.loc[start_row:end_row, "Date"]
        episode_data["Trading_Close"] = trading_df.loc[start_row:end_row, "Close"] # TODO: Include OHLC
        
        
        for query_params in query.queries:
            timeframe = query_params["timeframe"]
            window_size = query_params["window_size"]
            current_tf = self.timeframes[timeframe.lable]
            data_processor = query_params["data_processor"]
            
            valid = current_tf[self.time_column].isin(episode_data[self.time_column])
            #current_tf = current_tf.drop([self.time_column], axis=1)
            current_tf = pd.concat([current_tf.drop([self.time_column], axis=1).add_suffix(f"_{i}").shift(i) for i in range(window_size)], axis=1).dropna() # TODO: Add apply function
            current_tf = current_tf[valid]
            
            
            current_tf = current_tf.add_prefix(f"{timeframe.lable}_")
            print(current_tf.shape)
            episode_data = pd.concat([episode_data, current_tf], axis=1)    
        
        
        return episode_data
    
    def ohlc_processor(self, window: pd.DataFrame) -> pd.DataFrame:
        print(window)
        return window[window['Valid']]
        
        