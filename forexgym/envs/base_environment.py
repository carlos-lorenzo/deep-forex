from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
import gymnasium as gym


from ..utils import CurrencyPair, Query

from .episode import BaseEpisode
from .rewards import Reward

class BaseEnvironment(gym.Env):
    metadata = {'render_modes': ['ansi'], 'render_fps': None}
    
    def __init__(
        self, 
        currency_tickers: Dict[str, List[str]], 
        query: Query, 
        episode_length: int,
        reward_type: str,
        render_mode: str = None, 
        *args, 
        **kwargs
        ) -> None:
        
        time_column = kwargs.get("time_column", "Date")
        
        self.currency_pairs: Dict[str, CurrencyPair] = {ticker: CurrencyPair(ticker=ticker, timeframes=timeframes, time_column=time_column) for ticker, timeframes in currency_tickers.items()}
        self.datasets: Dict[str, pd.DataFrame] = {pair.ticker: pair.generate_dataset(query) for pair in self.currency_pairs.values()}
            
        self.render_mode = render_mode
    
        self.observation_space = gym.spaces.Box(
            low=-1e10, high=1e10, shape=(query.observation_size,), dtype=np.float32 
        )
        self.action_class = None
        self.action_space = None # Defined by child class
        self.episode_length = episode_length
        
        self.reward_type = Reward(reward_type)
        self.reward_range = self.reward_type.reward_range
        self.active_episode: BaseEpisode = BaseEpisode(episode_length=self.episode_length, datasets=self.datasets, reward_type=self.reward_type, *args, **kwargs)
          
    
    def _get_obs(self) -> np.ndarray:
        return self.active_episode.observation
    
    def _get_info(self) -> dict:
        return self.active_episode.info
    
    def reset(self, seed=None, options=None, *args, **kwargs) -> Tuple[np.ndarray, dict]:
        super().reset(seed=seed)
        
        self.active_episode.reset() # Episode initialization handled by Episode class
        
        observation = self._get_obs()
        info = self._get_info()
        
        return observation, info
    
    def step(self, action) -> Tuple[np.ndarray, float, bool, dict]:
          
        return self.active_episode.step(action)
    
    def render(self) -> None:
        return self.active_episode.render()
    
    def close(self) -> None:
        self.active_episode = None
        
        