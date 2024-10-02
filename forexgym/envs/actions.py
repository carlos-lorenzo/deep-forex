from typing import List

class DiscreteAction():
    def __init__(self, allow_holding: bool = False, max_length: int = 1) -> None:
        
        assert max_length > 0 
        
        self.allow_holding = allow_holding
        self.max_length = max_length
        
        self.action_space = list(range(-max_length, max_length + 1))
        if not allow_holding:
            self.action_space.pop(max_length)
    
    def valid_action(self, action: int) -> bool:
        return action in self.action_space
        
