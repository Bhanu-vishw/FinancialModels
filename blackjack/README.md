# Blackjack

This package implements a simplified version of the card game Blackjack. You can
find the full rules of the game
[here](https://bicyclecards.com/how-to-play/blackjack)

Here are the simplifications we're making:

- There are only two players: the dealer and the gambler (user of the game)
- Ace cards are only worth 11 (not 1 or 11)
- Splitting pairs, doubling down and insurance are not implemented

After installing this with

```shell
$ pip install -e .
```

You can play the game by invoking

```shell
$ blackjack_app
```