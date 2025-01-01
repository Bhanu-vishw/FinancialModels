from datetime import datetime

import backtestlib as bt
from backtestlib.portfolio import Portfolio


def test_portfolio_value_no_position():
    """Portfolio value with no positions should just be the cash amount"""
    cash = 1234567
    pf = bt.Portfolio(cash)
    assert pf.value() == cash
    assert len(pf.positions) == 0


def test_portfolio_apply_order_new_positions():
    """Applied orders create new positions if not tracked"""
    cash = 125000
    sym1, price1, qty1 = ("ABC", 150, 5)
    sym2, price2, qty2 = ("DEF", 500, -10)

    pf = bt.Portfolio(cash)
    pf.apply_order(sym1, price1, qty1)
    pf.apply_order(sym2, price2, qty2)

    assert len(pf.positions) == 2
    p1 = pf.positions.get(sym1)
    p2 = pf.positions.get(sym2)
    assert p1 is not None
    assert p2 is not None

    p1_value = p1.value(price1)
    assert p1_value == price1 * qty1
    p2_value = p2.value(price2)
    assert p2_value == price2 * qty2

    pf_value = pf.value({sym1: price1, sym2: price2})
    assert pf_value == cash
    assert pf.cash == cash - p1_value - p2_value


def test_portfolio_apply_order_update():
    """Applied orders should update existing positions"""
    cash = 125000
    sym1, price1, qty1 = ("ABC", 150, 5)
    sym2, price2, qty2 = ("ABC", 200, -5)

    pf = bt.Portfolio(cash)
    pf.apply_order(sym1, price1, qty1)
    pf.apply_order(sym2, price2, qty2)

    assert len(pf.positions) == 1
    pos = pf.positions.get(sym1)
    assert pos is not None

    # Closed position has no value
    arbitrary_price = 300
    assert pos.value(arbitrary_price) == 0
    assert pos.qty == 0
    # Closed position's realized gains/loses should be captured in cash
    assert pf.cash == cash - (price1 * qty1 + price2 * qty2)


def test_portfolio_on_event_caches():
    """Applied orders should update existing positions"""
    cash = 125000
    gain = 50
    sym, price, qty = ("ABC", 150, 5)

    pf = bt.Portfolio(cash)
    pf.apply_order(sym, price, qty)
    pf.on_event(bt.Event(1, datetime(2024, 10, 1), prices={sym: price + gain}))

    assert len(pf.positions) == 1
    assert pf.value() == cash + gain * qty
