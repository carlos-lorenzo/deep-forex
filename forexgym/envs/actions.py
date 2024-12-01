from typing import List

import numpy as np
from gymnasium.spaces import Discrete, Box


class DiscreteAction:
    def __init__(self, allow_holding: bool = False, max_length = 0) -> None:
        
        self.allow_holding = allow_holding
        
        self.action_space: List[int] = Discrete(n=2+int(allow_holding), start=-1)
        
    
    def valid_action(self, action: int) -> bool:
        return action in self.action_space
    


class ContinuousAction:
    def __init__(self) -> None:
        
        
        self.action_space: List[int] = Box(low=-1e10, high=1e10, shape=(1,), dtype=np.float32)
        
    
    def valid_action(self, action: int) -> bool:
        return action in self.action_space
    
