from .card import *


def _card_value(c: Card) -> int:
    """Helper function to calculate the value of a card. Aces and Face cards are
    worth 11, other cards are worth their numeric value"""
    # Your implementation
    if c.label in {Label.JACK, Label.QUEEN, Label.KING}:
        return 10
    elif c.label == Label.ACE:
        return 11 
    else:
        return c.label.value


class Hand:
    def __init__(self, card1: Card, card2: Card) -> None:
        """Initial deal"""
        self.cards = [card1, card2]

    def __repr__(self) -> str:
        """For debugging"""
        # Your implementation
        return f"Hand(cards={self.cards})"

    def total(self) -> int:
        """Tallies up the total of all the cards (can be > 21)"""
        # Your implementation
        return sum(_card_value(card) for card in self.cards)

    def value(self) -> int:
        """Value of all cards in deck (if bust is 0)"""
        # Your implementation
        total = self.total()
        aces_count = sum(1 for card in self.cards if card.label == Label.ACE) # Adjust for Aces if total is over 21

        while total > 21 and aces_count:
            total -= 10  # Treat one Ace as 1 instead of 11
            aces_count -= 1
        
        return total if total <= 21 else 0

    def hit(self, card: Card) -> None:
        """Hit by adding card to hand"""
        # Your implementation
        self.cards.append(card)

    def is_bust(self) -> bool:
        """Convenience function for whether hand is bust"""
        # Your implementation
        return self.value() == 0

    def is_blackjack(self) -> bool:
        """Convenience function for whether hand is a blackjack"""
        # Your implementation
        return self.value() == 21 and len(self.cards) == 2
