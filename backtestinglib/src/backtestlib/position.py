class Position:
    def __init__(self, symbol: str, qty: float) -> None:
        self.symbol = symbol
        self.qty = qty
    
    def value(self, price: float) -> float:
        """Market value of position given price"""
        # Your implementation
        return self.qty * price
