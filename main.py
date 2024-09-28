from forexgym import CurrencyPair, Query

if __name__ == "__main__":
    ticker = "EURUSD"
    #timeframes = ["1m", "5m", "15m", "30m", "1H", "4H", "1D"]
    timeframes = ["1H", "15m"]
    pair = CurrencyPair(ticker, timeframes)
    
    query = Query(episode_length=256, trading_timeframe="1H")
    query.add_query(
        timeframe="1H",
        window_size=3
    )
    query.add_query(
        timeframe="15m",
        window_size=4
    )
    episode = pair.query_episode(query)
    print(episode.head())
    