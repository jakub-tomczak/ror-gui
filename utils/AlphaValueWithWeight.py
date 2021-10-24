class AlphaValueWithWeight:
    def __init__(self, alpha_value: float, weight: float) -> None:
        self.alpha_value = alpha_value
        self.weight = weight
    
    def __repr__(self) -> str:
        return f'Alpha value: {self.alpha_value}, weight: {self.weight}'
