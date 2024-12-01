from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
import gymnasium as gym


from ..utils import CurrencyPair, Query

from .episode import ContinuousEpisode
from .actions import ContinuousAction
from .base_environment import BaseEnvironment


class ContinuousActionEnvironment(BaseEnvironment):
    def __init__(
        self, 
        currency_tickers: Dict[str, List[str]], 
        query: Query, 
        episode_length: int,
        reward_type: str,
        render_mode: str = None,
        hold_penalty: float = 0.01,
        reward_multiplier: float = 1.0,
        *args, 
        **kwargs
        ) -> None:
        
        super().__init__(currency_tickers=currency_tickers, query=query, episode_length=episode_length, reward_type=reward_type, render_mode=render_mode, *args, **kwargs)
        
        self.active_episode = ContinuousEpisode(episode_length=self.episode_length, datasets=self.datasets, reward_type=self.reward_type, reward_multiplier=reward_multiplier, *args, **kwargs)
        
        self.action_class = ContinuousAction()
        
        self.action_space = self.action_class.action_space
        
        self.hold_penalty = hold_penalty
        


     