import pytest

from blackjack.card import *


def test_card_init_unique_indexes():
    """Test that each card is assigned a unique index between 0 and 51. We don't
    really care how they're assigned but they must be unique."""
    card_indexes = []
    for suit in Suit:
        for label in Label:
            card_indexes.append(Card(suit, label).index)
    # sets are a type that just tracks unique values (like dictionary with only keys)
    card_index_set = set(card_indexes)
    assert len(card_indexes) == len(card_index_set)
    assert max(card_indexes) == 51
    assert min(card_indexes) == 0


def test_card_init_from_index_valid_range():
    """Test that from_index works within valid range"""
    for i in range(52):
        _ = Card.from_index(i)


def test_card_init_from_index_invalid_range_throws():
    """Test that from_index throws from outside the valid range"""
    with pytest.raises(ValueError):
        _ = Card.from_index(-1)
    with pytest.raises(ValueError):
        _ = Card.from_index(52)


def test_card_classifiers():
    """Test convenience functions"""
    for label in Label:
        for suit in Suit:
            c = Card(suit, label)
            if label == Label.ACE:
                assert c.is_ace()
                assert not c.is_face()
                assert not c.is_numeral()
            elif label in (Label.JACK, Label.QUEEN, Label.KING):
                assert not c.is_ace()
                assert c.is_face()
                assert not c.is_numeral()
            else:
                assert not c.is_ace()
                assert not c.is_face()
                assert c.is_numeral()


def test_label_str():
    """Test each label produces a string"""
    for label in Label:
        assert str(label) != None


def test_suit_str():
    """Test each suit produces a string"""
    for suit in Suit:
        assert str(suit) != None
