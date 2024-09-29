from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
import gymnasium as gym


from ..utils import CurrencyPair, Query

from .episode import BaseEpisode
from .rewards import Reward
from .base_environment import BaseEnvironment


class DiscreteEnvironment(BaseEnvironment):
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
        
        super().__init__(currency_tickers=currency_tickers, query=query, episode_length=episode_length, reward_type=reward_type, render_mode=render_mode, *args, **kwargs)