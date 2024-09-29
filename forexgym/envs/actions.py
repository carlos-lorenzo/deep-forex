from typing import List

class Action:
    def __init__(self, action) -> None:
        self.action = action
        
class DiscreteAction(Action):
    def __init__(self, action: int, allow_holding: bool = False, max_length: int = 1) -> None:
        
        assert max_length > 0 
        
        self.allow_holding = allow_holding
        self.max_length = max_length
        
        self.allowed_values = list(range(-max_length, max_length + 1))
        if not allow_holding:
            self.allowed_values.pop(max_length)
        
        assert action in self.allowed_values
        super().__init__(action)

class ContinuousAction(Action):
    def __init__(self, value: float) -> None:
        super().__init__(value)
