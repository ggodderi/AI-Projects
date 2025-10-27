"""Simple number guessing game.

Run this module directly to play the interactive game, or import
GuessingGame for programmatic use and testing.
"""
from __future__ import annotations

import random
from typing import Optional


class GuessingGame:
    """Core logic for the guessing game.

    Usage:
      game = GuessingGame(low=1, high=100, secret=42)  # deterministic
      result = game.guess(50)  # 'high' / 'low' / 'correct'
    """

    def __init__(self, low: int = 1, high: int = 100, secret: Optional[int] = None, seed: Optional[int] = None):
        if low >= high:
            raise ValueError("low must be less than high")
        self.low = low
        self.high = high
        self._rand = random.Random(seed)
        self._secret = secret if secret is not None else self._rand.randint(low, high)
        self.attempts = 0
        self._finished = False

    @property
    def secret(self) -> int:
        return self._secret

    @property
    def finished(self) -> bool:
        return self._finished

    def guess(self, value: int) -> str:
        """Make a guess and return one of: 'low', 'high', 'correct'.

        This increments the attempt counter. Raises TypeError if the
        provided value is not an int.
        """
        if not isinstance(value, int):
            raise TypeError("guess must be an int")
        if not (self.low <= value <= self.high):
            # Still count it as an attempt, but inform caller it's out of range.
            self.attempts += 1
            return "out-of-range"

        self.attempts += 1
        if value < self._secret:
            return "low"
        if value > self._secret:
            return "high"
        self._finished = True
        return "correct"


def main() -> None:
    """Run an interactive guessing game using stdin/stdout."""
    print("Welcome to the Guessing Game!")
    print("I'm thinking of a number between 1 and 100. Try to guess it.")
    game = GuessingGame(1, 100)

    while not game.finished:
        try:
            raw = input("Enter your guess (1-100): ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        raw = raw.strip()
        if raw == "":
            print("Please enter a number.")
            continue

        try:
            value = int(raw)
        except ValueError:
            print("That's not a valid integer. Try again.")
            continue

        result = game.guess(value)
        if result == "low":
            print("Too low — try a larger number.")
        elif result == "high":
            print("Too high — try a smaller number.")
        elif result == "out-of-range":
            print(f"{value} is outside the allowed range {game.low}-{game.high}.")
        else:  # correct
            print(f"Correct! You guessed the number in {game.attempts} attempts.")


if __name__ == "__main__":
    main()
