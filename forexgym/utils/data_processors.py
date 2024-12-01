from typing import Callable, Dict

import pandas as pd

from .timeframe import Timeframe, available_timeframes
from .query import Query

def default_processor(df: pd.DataFrame, time_column: str = "Date", *args, **kwargs) -> pd.DataFrame:
        """
            Drops the <time_column> column from an OHLC DataFrame. Default manipulation if no data_processor is provided in a query.

            Parameters:
                df (pd.DataFrame): The DataFrame from which to drop the <time_column> column.
                time_column (str): The name of the column to drop.
            
            Returns:
                pd.DataFrame: The OHLC with the <time_column> column removed.
        """
        
        return df.drop([time_column], axis=1)
    
    

def format_datasets(query: Query, timeframes: Dict[str, pd.DataFrame], time_column: str = "Date", *args, **kwargs) -> None:
        
    trading_timeframe_lable = query.trading_timeframe
    trading_timeframe = available_timeframes[trading_timeframe_lable]
    trading_column = query.trading_column
    
    trading_df = timeframes[trading_timeframe_lable]
    
    
    episode_data = pd.DataFrame()
    episode_data[time_column] = trading_df[time_column]
    episode_data["Trading_Price"] = trading_df[trading_column] # TODO: Include OHLC
    
    
    
    for query_params in query.queries:
        query_timeframe: Timeframe = query_params["timeframe"]
        window_size: int = query_params["window_size"]
        data_processor: Callable[[pd.DataFrame], pd.DataFrame] = query_params.get("data_processor", default_processor)
        
        # Selects the query dataframe
        query_df = timeframes[query_timeframe.lable]
        
        # Extracts features from the query dataframe
        processed_df = data_processor(query_df)
        
        # Creates a dataframe in which all rows contain all the features
        stacked = pd.concat([processed_df.add_suffix(f"_{shift}").shift(shift) for shift in range(window_size)], axis=1)
        
        # Smaller or equal than the trading TF
        if trading_timeframe >= query_timeframe:
            
            # Uses the existing dates in the trading dataframe to be included in the final datasets since all the other rows are irrelevant and will be discarded
            valid = query_df[time_column].isin(trading_df[time_column])
            
            # Selects the relevant rows (rows which share dates), adds a prefix and adds them to the final dataset
            filtered: pd.DataFrame = stacked[valid].reset_index(drop=True).add_prefix(f"{query_timeframe.lable}_")
            episode_data = pd.concat([episode_data, filtered], axis=1)
        
        # Greater TF than the trading TF 
        else:
            # Returns a pd.Series in which all dates of the trading dataframe have been rounded down to match that of the query (e.g. 12:00 -> 12:00, 12:15 -> 12:00, 12:30 -> 12:00, 12:45 -> 12:00)
            trading_dates = trading_df[time_column].copy().dt.floor(query_timeframe.value)
            
            # Includes the Date column back into the feature dataframe to be compared (the user probably has removed Date column from features)
            stacked[time_column] = query_df[time_column]
            
            # Given the trading dates (a series with Query Tf/Trading Tf n repeated rows 1H/15m = 4 repeated rows)
            # For each row (date) in trading dates the corresponding row (date) in the stacked dataframe is merged with the corresponding row (date) in the stacked dataframe such that the two rows share the same date
            # It therefore yields a dataframe consisting of merged rows with the same date so that for all divisiones in the trading TF it has data from the higher TFs
            # It is shifted n times to avoid lookahead bias
            # Ik its a bit confusing but it works
            
            
            filtered = pd.merge(trading_dates, stacked, on=time_column, how='outer').drop([time_column], axis=1).add_prefix(f"{query_timeframe.lable}_").shift(int(query_timeframe.value/trading_timeframe.value))
            
            # Filtered TF added horizontaly into the final dataset
            episode_data = pd.concat([episode_data, filtered], axis=1)
    
   
    episode_data = episode_data.dropna().reset_index(drop=True)
    
    
    
    return episode_data