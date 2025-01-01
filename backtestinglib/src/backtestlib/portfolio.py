from typing import Optional

from .event import Event
from .position import Position

class Portfolio:
    def __init__(self, cash: float) -> None:
        self.cash = cash
        self.positions: dict[str, Position] = {}
        self._latest_prices: dict[str, float] = {}

    def value(self, prices: Optional[dict[str, float]] = None) -> float:
        """Total market value of portfolio given current prices"""
        if prices is not None:
            self._latest_prices.update(prices)
        
        total_value = self.cash
        for symbol, position in self.positions.items():
            if position.qty == 0:  # Skip zero-quantity positions
                continue
                
            if symbol not in self._latest_prices:
                raise ValueError(f"No price available for non-zero position in {symbol}")
            
            total_value += position.value(self._latest_prices[symbol])
        
        return total_value

    def on_event(self, event: Event) -> None:
        """Cache the event"""
        # Your implementation
        if event.prices:  # Just check if the prices dict is non-empty
            self._latest_prices.update(event.prices)

    def apply_order(self, symbol: str, price: float, qty: float) -> None:
        """Update portfolio with order (negative qty indicates sell)"""
        # Your implementation
        
        order_value = price * qty
        
        # Check cash sufficiency for buys
        if qty > 0 and order_value > self.cash:
            raise ValueError(f"Insufficient cash for purchase: need {order_value}, have {self.cash}")
        
        # Check if sell would exceed position
        if qty < 0 and symbol in self.positions:
            if abs(qty) > self.positions[symbol].qty:
                raise ValueError(f"Insufficient position for sale: trying to sell {abs(qty)}, have {self.positions[symbol].qty}")
        
        # Update cash
        self.cash -= order_value
        
        # Update position
        if symbol in self.positions:
            self.positions[symbol].qty += qty
        else:
            self.positions[symbol] = Position(symbol, qty)
        
        # Update latest known price
        self._latest_prices[symbol] = price
