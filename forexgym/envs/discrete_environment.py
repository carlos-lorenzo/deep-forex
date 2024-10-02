from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
import gymnasium as gym


from ..utils import CurrencyPair, Query

from .episode import DiscreteEpisode
from .actions import DiscreteAction
from .base_environment import BaseEnvironment


class DiscreteActionEnvironment(BaseEnvironment):
    def __init__(
        self, 
        currency_tickers: Dict[str, List[str]], 
        query: Query, 
        episode_length: int,
        reward_type: str,
        render_mode: str = None,
        action_length: int = 1,
        allow_holding: bool = False,
        hold_penalty: float = 0.01,
        reward_multiplier: float = 1.0,
        *args, 
        **kwargs
        ) -> None:
        
        super().__init__(currency_tickers=currency_tickers, query=query, episode_length=episode_length, reward_type=reward_type, render_mode=render_mode, *args, **kwargs)
        
        self.active_episode = DiscreteEpisode(episode_length=self.episode_length, datasets=self.datasets, reward_type=self.reward_type, *args, **kwargs)
        
        self.action_class = DiscreteAction(allow_holding=allow_holding, max_length=action_length)
        
        self.action_space = self.action_class.action_space
        
        self.hold_penalty = hold_penalty
        
        self.reward_multiplier = reward_multiplier  

    def step(self, action) -> Tuple[np.ndarray, float, bool, dict]:
        assert self.action_class.valid_action(action) 
            
        observation, reward, done, info = self.active_episode.step(action)
        reward *= self.reward_multiplier
        if action == 0:
            reward = -self.hold_penalty
        
        return observation, reward, done, info