from enum import IntEnum
from typing import Optional

from .player import Dealer, Gambler


class Result(IntEnum):
    """Possible results for a round of Blackjack"""

    NATURAL_CASE_BOTH_BLACKJACK = 1
    NATURAL_CASE_GAMBLER_BLACKJACK = 2
    NATURAL_CASE_DEALER_BLACKJACK = 3
    GAMBLER_PLAY_BUST = 4
    DEALER_PLAY_BUST = 5
    SETTLEMENT_GAMBLER_WIN = 6
    SETTLEMENT_DEALER_WIN = 7
    SETTLEMENT_TIE = 8

    def __str__(self) -> str:
        match self.value:
            case self.NATURAL_CASE_BOTH_BLACKJACK:
                return "Gambler and dealer had blackjack on the deal, it's a wash 🧼🛁"
            case self.NATURAL_CASE_GAMBLER_BLACKJACK:
                return "Gambler had blackjack on the deal, woo! 🥳"
            case self.NATURAL_CASE_DEALER_BLACKJACK:
                return "Dealer had blackjack on the deal... 🤨"
            case self.GAMBLER_PLAY_BUST:
                return "Gambler went bust 😥"
            case self.DEALER_PLAY_BUST:
                return "Dealer went bust 😮‍💨"
            case self.SETTLEMENT_GAMBLER_WIN:
                return "Gambler has the better hand! 😊"
            case self.SETTLEMENT_DEALER_WIN:
                return "Dealer has the better hand... 🫠"
            case self.SETTLEMENT_TIE:
                return "Gambler and dealer have same hand, it's a wash 🧼🛁"


def play_round(gambler: Gambler, dealer: Dealer) -> Result:
    """Play a round of Blackjack"""
    # Your implementation
    bet = gambler.bet()
    
    # Deal initial hands
    dealer.deal_hands(gambler)

    # Check initial hand values
    gambler_value = gambler.hand.value()
    dealer_value = dealer.hand.value()

    # Handle natural blackjack cases
    if gambler_value == 21 and dealer_value == 21:
        gambler.receive(bet)  # Return bet on tie
        return Result.NATURAL_CASE_BOTH_BLACKJACK
    elif gambler_value == 21:
        gambler.receive(bet * 2)  # Win pays 1:1
        return Result.NATURAL_CASE_GAMBLER_BLACKJACK
    elif dealer_value == 21:
        return Result.NATURAL_CASE_DEALER_BLACKJACK

    # Gambler plays their hand
    gambler.play(dealer)
    
    # Check for gambler bust
    if gambler.hand.value() == 0:
        return Result.GAMBLER_PLAY_BUST

    # Dealer plays their hand
    dealer.play()
    
    # Check for dealer bust
    if dealer.hand.value() == 0:
        gambler.receive(bet * 2)
        return Result.DEALER_PLAY_BUST

    # Compare final hands for settlement
    final_gambler_value = gambler.hand.value()
    final_dealer_value = dealer.hand.value()

    if final_gambler_value > final_dealer_value:
        gambler.receive(bet * 2)  # Win pays 1:1
        return Result.SETTLEMENT_GAMBLER_WIN
    elif final_dealer_value > final_gambler_value:
        return Result.SETTLEMENT_DEALER_WIN
    else:
        gambler.receive(bet)  # Return bet on tie
        return Result.SETTLEMENT_TIE