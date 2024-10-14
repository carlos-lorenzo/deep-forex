from forexgym.utils import Query
from forexgym.envs import DiscreteActionEnvironment
import pandas as pd

def select_close(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    
    return pd.DataFrame(df["Close"])

def article_processor(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    df["x1"] = ((df["Close"].shift(-1) - df["Close"]) / df["Close"]).shift(1) 
    df["x2"] = ((df["High"].shift(-1) - df["High"]) / df["High"]).shift(1) 
    df["x3"] = ((df["Low"].shift(-1) - df["Low"]) / df["Low"]).shift(1) 
    df["x4"] = (df["High"] - df["Close"]) / df["Close"] 
    df["x5"] = (df["Close"] - df["Low"]) / df["Close"] 
    
    return df.drop(["Date", "Open", "High", "Low", "Close"], axis=1)

if __name__ == "__main__":
    ticker = "EURUSD"
    #timeframes = ["1m", "5m", "15m", "30m", "1H", "4H", "1D"]
    timeframes = ["1H", "15m"]
    
    query = Query(episode_length=256, trading_timeframe="15m", trading_column="Close")
    # query.add_query(
    #     timeframe="4H",
    #     window_size=4,
    #     data_processor=article_processor
    # )
    query.add_query(
        timeframe="1H",
        window_size=4,
        data_processor=article_processor
    )
    query.add_query(
        timeframe="15m",
        window_size=16,
        data_processor=article_processor
    )
    # dataset = pair.generate_dataset(query)
    
    env = DiscreteActionEnvironment(
        currency_tickers={"EURUSD": timeframes},
        query=query,
        reward_type="continuous",
        reward_multiplier=1e3,
        episode_length=256,
        allow_holding=True
    )
    
    #env.reset()
    #print(env.step(1))
    
    
    