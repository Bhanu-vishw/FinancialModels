from abc import ABC, abstractmethod
from typing import Optional

from .card import Card
from .deck import Deck
from .hand import Hand

__all__ = ("Gambler", "Dealer", "BettingStrategy", "PlayingStrategy")


class Player:
    def __init__(self) -> None:
        self.hand: Optional[Hand] = None

class Dealer(Player):
    def __init__(
        self, shuffle_at: Optional[int] = None, deck: Optional[Deck] = None
    ) -> None:
        super().__init__()
        self._deck = deck or Deck()
        self._shuffle_at = shuffle_at if shuffle_at is not None else 25

    def deal_hands(self, player: Player):
        """Generates the initial deal for the round. The dealer deals from the
        deck, starting with the player and alternating between player and self.
        The deck will be reset and reshuffled if it is below the shuffle_at
        threshold at the start of the deal.
        """
        if isinstance(player, Dealer):
            raise ValueError("Can't deal to another dealer")

        # Check if deck needs to be reset
        if self._deck.count() < self._shuffle_at:
            self._deck.reset()

        # Deal alternating between player and dealer
        # First card to player
        player_card1 = self._deck.deal()
        # First card to dealer
        dealer_card1 = self._deck.deal()
        # Second card to player
        player_card2 = self._deck.deal()
        # Second card to dealer
        dealer_card2 = self._deck.deal()

        # Create hands with dealt cards
        player.hand = Hand(player_card1, player_card2)
        self.hand = Hand(dealer_card1, dealer_card2)

    def up_card(self) -> Card:
        """The face up card that the gambler can see"""
        #return self.hand.cards[0]
        return self.hand.cards[0]

    def hit(self, hand: Hand) -> None:
        """Add a card to a hand"""
        # Your implementation
        if self._deck.count() == 0:
            self._deck.reset()
        card = self._deck.deal()
        hand.hit(card)

    def play(self) -> None:
        """Dealer play is formulaic and will hit if total < 17"""
        # Your implementation
        # while self.hand.value() < 17:
        #     self.hit(self.hand)
        while self.hand and self.hand.value() < 17 and not self.hand.is_bust():
            self.hit(self.hand)



class BettingStrategy(ABC):
    @abstractmethod
    def __call__(self, current_amount: int) -> int:
        """Decide how much to bet given current amount of cash. Returns the
        amount of the bet decided"""
        pass


class PlayingStrategy(ABC):
    @abstractmethod
    def __call__(self, gambler_hand: Hand, dealer: Dealer) -> None:
        """Derive to implement a strategy for how gambler should play given
        provided hand. Ask the dealer to hit the provided hand until
        satisfied, then return"""
        pass


class Gambler(Player):
    def __init__(
        self,
        bet_strategy: BettingStrategy,
        play_strategy: PlayingStrategy,
        initial_cash=1000,
    ) -> None:
        """Initialize a gambler with specified amount of cash"""
        super().__init__()
        self.cash = int(initial_cash)
        self.bet_strategy = bet_strategy
        self.play_strategy = play_strategy

    def bet(self) -> int:
        """Gambler bets according to strategy. Decrements the cash amount for
        the amount of the bet and returns the decided bet amount."""
        # Your implementation
        bet_amount = self.bet_strategy(self.cash)
        
        # Validate bet amount
        if bet_amount <= 0:
            raise ValueError("Bet must be greater than 0")
        if bet_amount > self.cash:
            raise ValueError("Insufficient funds to make this bet")
            
        self.cash -= bet_amount
        return bet_amount

    def receive(self, amount: int) -> None:
        """Add amount to gambler's cash level"""
        # Your implementation
        self.cash += amount

    def play(self, dealer: Dealer) -> None:
        """Gambler plays current hand according to strategy"""
        # Your implementation
        self.play_strategy(self.hand, dealer)
