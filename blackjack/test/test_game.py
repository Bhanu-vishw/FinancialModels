from typing import Iterable
from unittest import mock

from blackjack.card import *
from blackjack.deck import Deck
from blackjack.hand import Hand
from blackjack.player import *
from blackjack.game import Result, play_round


def test_result_str():
    """Test there's a valid string for each result enum"""
    for result in Result:
        assert str(result) is not None


# NOTE: these Game tests are a little closer to "integration" tests rather than
# unit tests since they test multiple components together. If you're passing
# these tests your game is likely working as expected


def test_game_natural_case_both_blackjack():
    """Test situation where there should be a natural wash"""
    bet_strategy: mock.MagicMock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.MagicMock = mock.create_autospec(PlayingStrategy)
    bet_amount = 10
    bet_strategy.return_value = bet_amount

    cards = (
        Card(Suit.CLUBS, Label.ACE),  # D2
        Card(Suit.DIAMONDS, Label.ACE),  # P2
        Card(Suit.CLUBS, Label.KING),  # D1
        Card(Suit.DIAMONDS, Label.KING),  # P1
    )
    deck = Deck(cards)
    gambler = Gambler(bet_strategy, play_strategy, initial_cash=10000)
    dealer = Dealer(shuffle_at=0, deck=deck)
    initial_cash = gambler.cash

    result = play_round(gambler, dealer)
    assert result == Result.NATURAL_CASE_BOTH_BLACKJACK
    assert gambler.cash == initial_cash
    bet_strategy.assert_called_once_with(initial_cash)
    play_strategy.assert_not_called()
    assert gambler.hand.value() == 21
    assert dealer.hand.value() == 21


def test_game_natural_case_gambler_blackjack():
    """Test situation where gambler wins from blackjack off of deal"""
    bet_strategy: mock.MagicMock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.MagicMock = mock.create_autospec(PlayingStrategy)
    bet_amount = 10
    bet_strategy.return_value = bet_amount

    cards = (
        Card(Suit.CLUBS, Label.JACK),  # D2
        Card(Suit.DIAMONDS, Label.KING),  # P2
        Card(Suit.CLUBS, Label.FIVE),  # D1
        Card(Suit.DIAMONDS, Label.ACE),  # P1
    )
    deck = Deck(cards)
    gambler = Gambler(bet_strategy, play_strategy, initial_cash=10000)
    dealer = Dealer(shuffle_at=0, deck=deck)
    initial_cash = gambler.cash

    result = play_round(gambler, dealer)
    assert result == Result.NATURAL_CASE_GAMBLER_BLACKJACK
    assert gambler.cash == initial_cash + bet_amount
    bet_strategy.assert_called_once_with(initial_cash)
    play_strategy.assert_not_called()
    assert gambler.hand.value() == 21
    assert dealer.hand.value() == 15


def test_game_natural_case_dealer_blackjack():
    """Test situation where dealer wins from blackjack off of deal"""
    bet_strategy: mock.MagicMock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.MagicMock = mock.create_autospec(PlayingStrategy)
    bet_amount = 10
    bet_strategy.return_value = bet_amount

    cards = (
        Card(Suit.CLUBS, Label.JACK),  # D2
        Card(Suit.DIAMONDS, Label.KING),  # P2
        Card(Suit.CLUBS, Label.ACE),  # D1
        Card(Suit.DIAMONDS, Label.FIVE),  # P1
    )
    deck = Deck(cards)
    gambler = Gambler(bet_strategy, play_strategy, initial_cash=10000)
    dealer = Dealer(shuffle_at=0, deck=deck)
    initial_cash = gambler.cash

    result = play_round(gambler, dealer)
    assert result == Result.NATURAL_CASE_DEALER_BLACKJACK
    assert gambler.cash == initial_cash - bet_amount
    bet_strategy.assert_called_once_with(initial_cash)
    play_strategy.assert_not_called()
    assert gambler.hand.value() == 15
    assert dealer.hand.value() == 21


def test_game_gambler_play_bust():
    """Test situation where gambler busts on the play"""
    bet_strategy: mock.MagicMock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.MagicMock = mock.create_autospec(PlayingStrategy)
    # Mock up gambler strategy to hit once to get P3
    play_strategy.side_effect = lambda h, d: d.hit(h)
    bet_amount = 10
    bet_strategy.return_value = bet_amount

    cards = (
        Card(Suit.HEARTS, Label.KING),  # P3
        Card(Suit.CLUBS, Label.JACK),  # D2
        Card(Suit.DIAMONDS, Label.TEN),  # P2
        Card(Suit.CLUBS, Label.TWO),  # D1
        Card(Suit.DIAMONDS, Label.FIVE),  # P1
    )
    deck = Deck(cards)
    gambler = Gambler(bet_strategy, play_strategy, initial_cash=10000)
    dealer = Dealer(shuffle_at=0, deck=deck)
    initial_cash = gambler.cash

    result = play_round(gambler, dealer)
    assert result == Result.GAMBLER_PLAY_BUST
    assert gambler.cash == initial_cash - bet_amount
    bet_strategy.assert_called_once_with(initial_cash)
    play_strategy.assert_called_once()
    assert gambler.hand.value() == 0
    assert dealer.hand.value() == 12


def test_game_dealer_play_bust():
    """Test situation where dealer busts on the play"""
    bet_strategy: mock.MagicMock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.MagicMock = mock.create_autospec(PlayingStrategy)
    bet_amount = 10
    bet_strategy.return_value = bet_amount

    cards = (
        Card(Suit.CLUBS, Label.QUEEN),  # D3 (dealer must hit and get this at < 17)
        Card(Suit.CLUBS, Label.TEN),  # D2
        Card(Suit.DIAMONDS, Label.TEN),  # P2
        Card(Suit.CLUBS, Label.SIX),  # D1
        Card(Suit.DIAMONDS, Label.FIVE),  # P1
    )
    deck = Deck(cards)
    gambler = Gambler(bet_strategy, play_strategy, initial_cash=10000)
    dealer = Dealer(shuffle_at=0, deck=deck)
    initial_cash = gambler.cash

    result = play_round(gambler, dealer)
    assert result == Result.DEALER_PLAY_BUST
    assert gambler.cash == initial_cash + bet_amount
    bet_strategy.assert_called_once_with(initial_cash)
    play_strategy.assert_called_once()
    assert gambler.hand.value() == 15
    assert dealer.hand.value() == 0


def test_game_settlement_gambler_win():
    """Test situation where gambler wins on the settlement"""
    bet_strategy: mock.MagicMock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.MagicMock = mock.create_autospec(PlayingStrategy)
    # We'll have them reach this settlement through playing
    play_strategy.side_effect = lambda h, d: d.hit(h)
    bet_amount = 10
    bet_strategy.return_value = bet_amount

    cards = (
        Card(Suit.CLUBS, Label.TWO),  # D3
        Card(Suit.CLUBS, Label.FIVE),  # P3
        Card(Suit.CLUBS, Label.TEN),  # D2
        Card(Suit.DIAMONDS, Label.TEN),  # P2
        Card(Suit.CLUBS, Label.SIX),  # D1
        Card(Suit.DIAMONDS, Label.FIVE),  # P1
    )
    deck = Deck(cards)
    gambler = Gambler(bet_strategy, play_strategy, initial_cash=10000)
    dealer = Dealer(shuffle_at=0, deck=deck)
    initial_cash = gambler.cash

    result = play_round(gambler, dealer)
    assert result == Result.SETTLEMENT_GAMBLER_WIN
    assert gambler.cash == initial_cash + bet_amount
    bet_strategy.assert_called_once_with(initial_cash)
    play_strategy.assert_called_once()
    assert gambler.hand.value() == 20
    assert dealer.hand.value() == 18


def test_game_settlement_dealer_win():
    """Test situation where dealer wins on the settlement"""
    bet_strategy: mock.MagicMock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.MagicMock = mock.create_autospec(PlayingStrategy)
    bet_amount = 10
    bet_strategy.return_value = bet_amount

    cards = (
        Card(Suit.CLUBS, Label.KING),  # D2
        Card(Suit.DIAMONDS, Label.TEN),  # P2
        Card(Suit.CLUBS, Label.TEN),  # D1
        Card(Suit.DIAMONDS, Label.FIVE),  # P1
    )
    deck = Deck(cards)
    gambler = Gambler(bet_strategy, play_strategy, initial_cash=10000)
    dealer = Dealer(shuffle_at=0, deck=deck)
    initial_cash = gambler.cash

    result = play_round(gambler, dealer)
    assert result == Result.SETTLEMENT_DEALER_WIN
    assert gambler.cash == initial_cash - bet_amount
    bet_strategy.assert_called_once_with(initial_cash)
    play_strategy.assert_called_once()
    assert gambler.hand.value() == 15
    assert dealer.hand.value() == 20


def test_game_settlement_tie():
    """Test situation where there's a tie on the settlement"""
    bet_strategy: mock.MagicMock = mock.create_autospec(BettingStrategy)
    play_strategy: mock.MagicMock = mock.create_autospec(PlayingStrategy)
    bet_amount = 10
    bet_strategy.return_value = bet_amount

    cards = (
        Card(Suit.CLUBS, Label.KING),  # D2
        Card(Suit.DIAMONDS, Label.TEN),  # P2
        Card(Suit.CLUBS, Label.TEN),  # D1
        Card(Suit.DIAMONDS, Label.KING),  # P1
    )
    deck = Deck(cards)
    gambler = Gambler(bet_strategy, play_strategy, initial_cash=10000)
    dealer = Dealer(shuffle_at=0, deck=deck)
    initial_cash = gambler.cash

    result = play_round(gambler, dealer)
    assert result == Result.SETTLEMENT_TIE
    assert gambler.cash == initial_cash
    bet_strategy.assert_called_once_with(initial_cash)
    play_strategy.assert_called_once()
    assert gambler.hand.value() == 20
    assert dealer.hand.value() == 20
