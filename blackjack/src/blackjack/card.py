from enum import IntEnum

__all__ = ("Card", "Suit", "Label")


class Suit(IntEnum):
    HEARTS = 1
    DIAMONDS = 2
    CLUBS = 3
    SPADES = 4

    def __str__(self) -> str:
        """Your implementation"""
        return self.name

class Label(IntEnum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

    def __str__(self) -> str:
        """Your implementation"""
        return self.name


def _to_index(suit: Suit, label: Label) -> int:
    """Given a suit and label returns the index in a 52 card deck (0...51)"""
    # Your implementation
    return (label.value - 1) * 4 + (suit.value - 1)


def _from_index(index: int) -> tuple[Suit, Label]:
    """Create a Suit and Label given a numeric index"""
    # Your implementation
    label_value = (index // 4) + 1
    suit_value = (index % 4) + 1
    return Suit(suit_value), Label(label_value)


class Card:
    @classmethod
    def from_index(cls, index: int) -> "Card":
        """Return a card given an index"""
        # Your implementation
        suit, label = _from_index(index)
        return cls(suit, label)

    def __init__(self, suit: Suit, label: Label) -> None:
        """Initialize 'suit', 'label', and 'index' members"""
        # Your implementation
        self.suit = suit
        self.label = label
        self.index = _to_index(suit, label)

    def __repr__(self) -> str:
        """For debugging"""
        # Your implementation
        return f"Card(suit={self.suit}, label={self.label}, index={self.index})"

    def __str__(self) -> str:
        """For pretty print"""
        # Your implementation
        return f"{self.label} of {self.suit}"

    def is_face(self) -> bool:
        """Returns true if is a face card"""
        # Your implementation
        return self.label in {Label.JACK, Label.QUEEN, Label.KING}

    def is_ace(self) -> bool:
        """Returns true if is an Ace"""
        # Your implementation
        return self.label == Label.ACE

    def is_numeral(self) -> bool:
        """If numbered i.e. 'pip' card, 2-10"""
        # Your implementation
        return Label.TWO <= self.label <= Label.TEN
