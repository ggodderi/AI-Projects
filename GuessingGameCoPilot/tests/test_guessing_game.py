import pytest

from guessing_game import GuessingGame


def test_correct_first_try():
    game = GuessingGame(low=1, high=100, secret=42)
    res = game.guess(42)
    assert res == "correct"
    assert game.attempts == 1
    assert game.finished is True


def test_low_then_high_then_correct():
    game = GuessingGame(low=1, high=100, secret=50)
    assert game.guess(25) == "low"
    assert game.attempts == 1
    assert game.guess(75) == "high"
    assert game.attempts == 2
    assert game.guess(50) == "correct"
    assert game.attempts == 3


def test_out_of_range_counts_as_attempt():
    game = GuessingGame(low=1, high=10, secret=5)
    assert game.guess(20) == "out-of-range"
    assert game.attempts == 1


def test_type_error_on_non_int():
    game = GuessingGame(low=1, high=100, secret=10)
    with pytest.raises(TypeError):
        game.guess("not-an-int")
