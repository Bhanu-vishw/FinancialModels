from dataclasses import dataclass

from datetime import datetime


@dataclass
class Event:
    number: int
    """Event number"""

    timestamp: datetime
    """Time of event"""

    prices: dict[str, float]
    """Prices for each symbol"""
