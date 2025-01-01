import random
from typing import Optional, Iterable, Self

from .card import *

class Deck:
    def __init__(self, cards: Optional[Iterable[Card]] = None) -> None:
        """Initializes a deck with 52 shuffled cards by default or specific
        cards if specified"""
        # Your implementation
        if cards is None: # Create a standard 52-card deck
            self.cards = [Card.from_index(i) for i in range(52)]
            self.indexes = list(range(52))
        else:
            self.cards = list(cards)
            self.indexes = [card.index for card in self.cards]
    
        if cards is None: # Only shuffle for default deck
            self.shuffle()

    def count(self):
        """Number of cards currently in the deck"""
        # Your implementation
        return len(self.cards)

    def reset(self):
        """Resets the deck to the original 52 cards"""
        # Your implementation
        self.cards = [Card.from_index(i) for i in range(52)]
        self.indexes = list(range(52))
        self.shuffle()

    def shuffle(self):
        """Shuffles existing cards"""
        # Your implementation
        combined = list(zip(self.cards, self.indexes))    # Keep shuffling until we get a different order 
        original_indexes = self.indexes.copy()
        while self.indexes == original_indexes:
            random.shuffle(combined)
            self.cards, self.indexes = zip(*combined)
            self.cards = list(self.cards)
            self.indexes = list(self.indexes)

    def deal(self) -> Card:
        """Deals a card from the deck"""
        # Your implementation
        self.indexes.pop()
        return self.cards.pop()
