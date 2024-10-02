from typing import Dict, Tuple
import random

import pandas as pd

from .actions import DiscreteAction
from .rewards import Reward

class BaseEpisode:
    def __init__(self, episode_length: int, datasets: Dict[str, pd.DataFrame], reward_type: Reward, time_column: str = "Date") -> None:
        self.episode_length: int = episode_length
        
        self.datasets = datasets
        self.dataset: pd.DataFrame = None
        
        self.time_step: int = None
        self.active_ticker: str = None
        
        self.reward_type = reward_type
        self.time_column = time_column
        
        self._generate_episode_dataframe(episode_length, time_column)
        
    def _generate_episode_dataframe(self, episode_length: int, time_column: str = "Date") -> None:
        ticker, dataset = random.choice(list(self.datasets.items()))
        
        # dataset = dataset.drop(["Trading_Price"], axis=1)
        start_index = dataset[:-episode_length].sample(n=1).index[0]
        
        self.dataset = dataset[start_index:start_index+episode_length]
        self.active_ticker = ticker
    
    def reset(self):
        self.time_step = 0
        
        self._generate_episode_dataframe(self.episode_length, self.datasets)
        
        return self.observation, self.info
    
    def step(self, action) -> Tuple[pd.DataFrame, float, bool, dict]:
        raise NotImplementedError("Each child class must implement this method")
    
    def render(self) -> dict:
        return self.info
    
    @property
    def observation(self):
        return self.dataset.drop(["Trading_Price", self.time_column], axis=1).iloc[self.time_step].to_numpy()
    
    @property
    def info(self) -> dict:
        return {"time_step": self.time_step, "ticker": self.active_ticker}
    
    @property
    def done(self) -> bool:
        return self.time_step >= self.episode_length
    


class DiscreteEpisode(BaseEpisode):
    def __init__(self, episode_length: int, datasets: Dict[str, pd.DataFrame], reward_type: Reward, allow_holding: bool = False, action_length: int = 1, *args, **kwargs) -> None:
        super().__init__(episode_length=episode_length, datasets=datasets, reward_type=reward_type, *args, **kwargs)
        self.allow_holding = allow_holding
        self.action_length = action_length
        
    
    def step(self, action) -> Tuple[pd.DataFrame, float, bool, dict]:
        start_rate = self.dataset.iloc[self.time_step]["Trading_Price"]
        self.time_step += 1
        end_rate = self.dataset.iloc[self.time_step]["Trading_Price"]
        
        
        if self.allow_holding and action == 0:
            reward = 0
        
        else:
            bought = action > 0
            reward = self.reward_type.reward(start_rate=start_rate, end_rate=end_rate, bought=bought)
        
        return self.observation, reward, self.done, self.info