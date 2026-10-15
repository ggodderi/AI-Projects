# Guessing Game

Simple number guessing game in Python.

How to run:

PowerShell (Windows):

```powershell
python guessing_game.py
```

What it does:
- Picks a random number between 1 and 100.
- Prompts the user to guess until correct.
- Tells the user if a guess is too low or too high and shows total attempts when guessed correctly.

You can supply custom bounds when the game starts. The CLI will prompt you for a minimum and maximum number (defaults: 1 and 100). Press Enter to accept a default.

Running tests:

```powershell
python -m pip install pytest
python -m pytest -q
```
