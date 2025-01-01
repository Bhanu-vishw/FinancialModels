from unittest import mock

import pytest

from blackjack.card import *
from blackjack.deck import Deck
from blackjack.hand import Hand
from blackjack.player import *


def test_dealer_deal_hands():
    """Test hands get dealt to gambler and dealer"""
    bet_strategy: mock.Mock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.Mock = mock.create_autospec(PlayingStrategy)
    gambler = Gambler(bet_strategy, play_strategy)
    dealer = Dealer()

    # Initially there should be no hand
    assert gambler.hand is None
    assert dealer.hand is None

    dealer.deal_hands(gambler)
    dh1 = dealer.hand
    gh1 = gambler.hand
    assert isinstance(dh1, Hand)
    assert isinstance(gh1, Hand)

    # Check now that next deal is different
    dealer.deal_hands(gambler)
    assert isinstance(dealer.hand, Hand)
    assert isinstance(gambler.hand, Hand)
    assert dealer.hand != dh1
    assert gambler.hand != gh1


def test_dealer_shuffles():
    """Test that at specified threshold dealer will shuffle"""
    bet_strategy: mock.Mock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.Mock = mock.create_autospec(PlayingStrategy)
    gambler = Gambler(bet_strategy, play_strategy)

    # Low enough to not shuffle after first rounds, we can check that indexes
    # haven't changed
    deck = Deck()
    initial_indexes = deck.indexes
    dealer = Dealer(shuffle_at=20, deck=deck)
    dealer.deal_hands(gambler)
    dealer.deal_hands(gambler)
    dealer.deal_hands(gambler)
    assert deck.indexes == initial_indexes

    # Now force a shuffle after the first hand
    deck = Deck()
    initial_indexes = deck.indexes
    dealer = Dealer(shuffle_at=50, deck=deck)
    dealer.deal_hands(gambler)
    dealer.deal_hands(gambler)
    assert deck.indexes != initial_indexes


def test_dealer_hit():
    """Test dealer hit method applies card to hand"""
    c1 = Card(Suit.CLUBS, Label.EIGHT)
    c2 = Card(Suit.DIAMONDS, Label.SIX)
    hand = Hand(c1, c2)
    dealer = Dealer()
    dealer.hit(hand)
    assert hand.cards[:2] == [c1, c2]
    assert len(hand.cards) == 3


def test_dealer_play_hits_lt_17():
    """Test that dealer hits if under 17"""
    c1 = Card(Suit.CLUBS, Label.TEN)
    c2 = Card(Suit.DIAMONDS, Label.THREE)
    # We could use the Deck's constructor to pass in a specific set of cards,
    # but using a Mock object is another way to get the deck to deal us specific
    # cards
    deck: mock.MagicMock = mock.create_autospec(Deck)
    deck.deal.side_effect = [
        Card(Suit.DIAMONDS, Label.TWO),
        Card(Suit.CLUBS, Label.THREE),
    ]
    dealer = Dealer(deck=deck)
    dealer.hand = Hand(c1, c2)
    dealer.play()
    assert deck.deal.call_count == 2
    assert dealer.hand.value() == 18


def test_dealer_play_stays_gte_17():
    """Test that dealer stays if dealt hand greater than or equal to 17"""
    c1 = Card(Suit.CLUBS, Label.TEN)
    c2 = Card(Suit.DIAMONDS, Label.SEVEN)
    deck: mock.MagicMock = mock.create_autospec(Deck)
    dealer = Dealer(deck=deck)
    dealer.hand = Hand(c1, c2)
    dealer.play()
    deck.deal.assert_not_called()
    assert dealer.hand.value() == 17


def test_gambler_bet():
    """Test betting ranges"""
    bet_strategy: mock.MagicMock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.MagicMock = mock.create_autospec(PlayingStrategy)

    # Legit bet
    bet_strategy.return_value = 5
    gambler = Gambler(bet_strategy, play_strategy, initial_cash=1000)
    assert gambler.bet() == 5
    assert gambler.cash == 995

    # Too high of bet should raise an exception
    bet_strategy.return_value = 1001
    gambler = Gambler(bet_strategy, play_strategy, initial_cash=1000)
    with pytest.raises(ValueError):
        _ = gambler.bet()
    assert gambler.cash == 1000

    # Too low of bet should raise an exception
    bet_strategy.return_value = 0
    gambler = Gambler(bet_strategy, play_strategy, initial_cash=1000)
    with pytest.raises(ValueError):
        _ = gambler.bet()
    assert gambler.cash == 1000


def test_gambler_play():
    """Test that provided playing strategy gets invoked"""
    bet_strategy: mock.Mock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.Mock = mock.create_autospec(PlayingStrategy)
    gambler = Gambler(bet_strategy, play_strategy)
    gambler.play(Dealer())
    play_strategy.assert_called_once()
