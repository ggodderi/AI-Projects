AI Sudoku 1

This is a minimal Python GUI Sudoku player created to satisfy the instructions in Description1.txt.

Files:
- ai_sudoku1.py: The main tkinter GUI application. Run with `python ai_sudoku1.py`.
 - ai_sudoku2.py / ai_sudoku3.py: Alternate versions; `ai_sudoku3.py` includes Save/Load game support.

Usage notes:
- Click a non-given cell to select it, type 1-9 to place a number, press Backspace/Delete or 0 to clear.
- "New Puzzle" loads a random embedded puzzle.
- "Hint" shows valid candidate numbers for the selected empty cell.
- "Check" verifies the filled grid and reports whether the solution is correct.
 - Original (given) cells are shaded light gray to distinguish them from user-entered values.
 - `ai_sudoku3.py` adds Save and Load buttons to persist the current game to a JSON file and load it later.

Requirements: standard Python (tested on 3.10) with tkinter available (usually included).
