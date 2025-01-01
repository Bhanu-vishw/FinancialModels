from .game import play_round, Result
from .hand import Hand
from .player import *

__all__ = ("main",)


def get_input_str(prompt: str, lower_case: bool = True) -> str:
    """Simple wrapper to get input, stripping whitespace"""
    result = input(f"{prompt}\n> ").strip()
    if lower_case:
        result = result.lower()
    return result


def print_title(msg: str) -> None:
    bold_cyan = "\033[1m\033[96m"
    end = "\033[0m"
    frame = "-" * len(msg)
    print(f"{bold_cyan}{frame}{end}")
    print(f"{bold_cyan}{msg}{end}")
    print(f"{bold_cyan}{frame}{end}")


def print_header(msg: str) -> None:
    bold_cyan = "\033[1m\033[96m"
    end = "\033[0m"
    print(f"{bold_cyan}{msg}{end}")


def print_msg(msg: str) -> None:
    print(msg)


def print_result(
    round_num: int, result: Result, gambler: Gambler, dealer: Dealer
) -> None:
    print_msg(
        f"""
    Round {round_num} result: ({result})
        Gambler hand: {gambler.hand} ({gambler.hand.value()})
        Dealer hand: {dealer.hand} ({dealer.hand.value()})
        Cash after bet: {gambler.cash}
    """.strip()
    )


class InputBettingStrategy(BettingStrategy):
    def __call__(self, current_cash: int) -> int:
        print_header("Decide bet")
        while True:
            result = get_input_str(f"How much to bet? (cash={current_cash})?")
            if result.isdigit():
                return int(result)
            else:
                print_msg(f"'{result}' needs to be an integer, please try again!")


class InputPlayingStrategy(PlayingStrategy):
    def __call__(self, gambler_hand: Hand, dealer: Dealer) -> None:
        print_header("Play hand")
        print_msg(f"The dealer face up card is: {dealer.up_card()}")
        while gambler_hand.total() < 21:
            print_msg(f"Current hand: {gambler_hand} (value={gambler_hand.value()})")
            result = get_input_str(f"What would you like to do? (hit/stay)")
            if result == "hit":
                dealer.hit(gambler_hand)
            elif result == "stay":
                break
            else:
                print_msg("I don't understand :(, please enter 'hit' or 'stay'")


def main():
    print_title("Blackjack v0.0.1")
    print_msg("Welcome to Blackjack!")
    print_msg("You can exit this game at any time by hitting Ctrl+C")
    try:
        amount = None
        while amount is None:
            result = input("How many chips would you like to buy?\n> ")
            if result.isdigit():
                amount = int(result)
            else:
                print_msg(f"{result} is invalid (integer amount is required)")

        gambler = Gambler(InputBettingStrategy(), InputPlayingStrategy(), amount)
        dealer = Dealer()

        print_msg("Okay then! Let's get started")
        i = 1
        while True:
            print_title(f"Round {i}")
            result = play_round(gambler, dealer)
            print_header("Round is complete")
            print_result(i, result, gambler, dealer)
            i += 1
    except KeyboardInterrupt:
        print_msg("\nI see you've had enough... see you later 🙂")


if __name__ == "__main__":
    main()
