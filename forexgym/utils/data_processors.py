import pandas as pd

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