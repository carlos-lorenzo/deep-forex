from typing import Tuple

class Reward:
    def __init__(self, reward_type: str = "categorical") -> None:
        
        
        self.reward_type = reward_type
        
        self.allowed_types = ["categorical", "continuous"]
        
        if self.reward_type not in self.allowed_types:
            raise ValueError(f"Reward type must be one of {self.allowed_types}")
        
    
    def reward(self, start_rate: float, end_rate: float, bought: bool,) -> float:
        if self.reward_type == "categorical":
            if bought and start_rate < end_rate:
                return 1
            else:
                return -1
        elif self.reward_type == "continuous":
            if bought and start_rate < end_rate:
                return end_rate - start_rate
            else:
                return start_rate - end_rate
            
    @property
    def reward_range(self) -> Tuple[float, float]:
        if self.reward_type == "categorical":
            return (-1, 1)
        elif self.reward_type == "continuous":
            return (-1e10, 1e10)