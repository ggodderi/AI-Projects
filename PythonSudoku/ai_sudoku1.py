"""
ai_sudoku1.py
A simple GUI Sudoku player using tkinter.

Features implemented from Description1.txt:
1) Load random puzzles from an embedded list
2) Click on a cell and enter a number (keyboard 1-9 or delete/0 to clear)
3) Inform the user if the number entered is invalid (out of range or violates row/col/region)
4) Hint button: shows possible candidates for the currently selected cell
5) When all cells are filled, checks whether the puzzle is correct and reports success/failure

Usage:
python ai_sudoku1.py

This is a single-file, minimal implementation suitable for local use.
"""

import tkinter as tk
from tkinter import messagebox
import random

# A few sample puzzles (0 = empty). Each puzzle is a 9x9 list of lists.
SAMPLE_PUZZLES = [
    # Easy puzzle
    [
        [5,3,0,0,7,0,0,0,0],
        [6,0,0,1,9,5,0,0,0],
        [0,9,8,0,0,0,0,6,0],
        [8,0,0,0,6,0,0,0,3],
        [4,0,0,8,0,3,0,0,1],
        [7,0,0,0,2,0,0,0,6],
        [0,6,0,0,0,0,2,8,0],
        [0,0,0,4,1,9,0,0,5],
        [0,0,0,0,8,0,0,7,9],
    ],
    # Another puzzle
    [
        [0,0,0,2,6,0,7,0,1],
        [6,8,0,0,7,0,0,9,0],
        [1,9,0,0,0,4,5,0,0],
        [8,2,0,1,0,0,0,4,0],
        [0,0,4,6,0,2,9,0,0],
        [0,5,0,0,0,3,0,2,8],
        [0,0,9,3,0,0,0,7,4],
        [0,4,0,0,5,0,0,3,6],
        [7,0,3,0,1,8,0,0,0],
    ],
]

CELL_SIZE = 50
GRID_PAD = 20

class SudokuGUI:
    def __init__(self, master):
        self.master = master
        master.title("AI Sudoku 1")
        self.canvas = tk.Canvas(master, width=9*CELL_SIZE+2*GRID_PAD, height=9*CELL_SIZE+2*GRID_PAD)
        self.canvas.pack()

        self.selected = None  # (r,c)
        self.puzzle = []
        self.solution = None
        self.original = []  # which cells are given

        # Controls
        frame = tk.Frame(master)
        frame.pack(pady=10)
        tk.Button(frame, text="New Puzzle", command=self.load_random_puzzle).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Hint", command=self.show_hint).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Check", command=self.check_complete).pack(side=tk.LEFT, padx=5)

        # Bindings
        self.canvas.bind("<Button-1>", self.on_click)
        master.bind("<Key>", self.on_key)

        self.load_random_puzzle()

    def load_random_puzzle(self):
        puzzle = random.choice(SAMPLE_PUZZLES)
        # Deep copy
        self.puzzle = [row[:] for row in puzzle]
        self.original = [[bool(cell) for cell in row] for row in puzzle]
        self.selected = None
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        pad = GRID_PAD
        for r in range(9):
            for c in range(9):
                x1 = pad + c*CELL_SIZE
                y1 = pad + r*CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                cell_tag = f"cell_{r}_{c}"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill='white', tags=(cell_tag,))
                val = self.puzzle[r][c]
                if val != 0:
                    color = 'black' if self.original[r][c] else 'blue'
                    self.canvas.create_text(x1+CELL_SIZE/2, y1+CELL_SIZE/2, text=str(val), fill=color, font=(None, 16), tags=(cell_tag,))
        # thicker lines for 3x3
        for i in range(10):
            width = 1
            if i%3==0:
                width = 3
            x = pad + i*CELL_SIZE
            self.canvas.create_line(x, pad, x, pad+9*CELL_SIZE, width=width)
            y = pad + i*CELL_SIZE
            self.canvas.create_line(pad, y, pad+9*CELL_SIZE, y, width=width)
        if self.selected:
            self.highlight_selected()

    def on_click(self, event):
        pad = GRID_PAD
        x = event.x - pad
        y = event.y - pad
        if x<0 or y<0 or x>9*CELL_SIZE or y>9*CELL_SIZE:
            return
        c = x // CELL_SIZE
        r = y // CELL_SIZE
        r = int(r); c = int(c)
        if self.original[r][c]:
            # can't select given cells
            self.selected = None
        else:
            self.selected = (r,c)
        self.draw_grid()

    def highlight_selected(self):
        r,c = self.selected
        pad = GRID_PAD
        x1 = pad + c*CELL_SIZE
        y1 = pad + r*CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=3)

    def on_key(self, event):
        if not self.selected:
            return
        key = event.char
        if key in '123456789':
            num = int(key)
            r,c = self.selected
            if self.is_valid_move(r,c,num):
                self.puzzle[r][c] = num
                self.draw_grid()
                if self.is_filled():
                    self.check_complete()
            else:
                messagebox.showinfo("Invalid", f"{num} is not a valid entry at that cell.")
        elif key in ('0', '\b', '\x7f'):
            r,c = self.selected
            self.puzzle[r][c] = 0
            self.draw_grid()

    def is_valid_move(self, r, c, num):
        if not (1 <= num <= 9):
            return False
        # Check row
        for j in range(9):
            if self.puzzle[r][j] == num and j!=c:
                return False
        # Check col
        for i in range(9):
            if self.puzzle[i][c] == num and i!=r:
                return False
        # Check 3x3
        br = (r//3)*3
        bc = (c//3)*3
        for i in range(br, br+3):
            for j in range(bc, bc+3):
                if self.puzzle[i][j] == num and (i,j)!=(r,c):
                    return False
        return True

    def possible_options(self, r, c):
        if self.original[r][c]:
            return []
        if self.puzzle[r][c]!=0:
            return []
        opts = []
        for num in range(1,10):
            if self.is_valid_move(r,c,num):
                opts.append(num)
        return opts

    def show_hint(self):
        if not self.selected:
            messagebox.showinfo("Hint", "Select a non-given empty cell to get options.")
            return
        r,c = self.selected
        if self.original[r][c]:
            messagebox.showinfo("Hint", "This is a given cell.")
            return
        if self.puzzle[r][c]!=0:
            messagebox.showinfo("Hint", "Cell already has a number. Clear it first to see options.")
            return
        opts = self.possible_options(r,c)
        if not opts:
            messagebox.showinfo("Hint", "No valid options for this cell (puzzle may be invalid).")
        else:
            messagebox.showinfo("Hint", f"Possible options: {opts}")

    def is_filled(self):
        for i in range(9):
            for j in range(9):
                if self.puzzle[i][j]==0:
                    return False
        return True

    def check_complete(self):
        if not self.is_filled():
            messagebox.showinfo("Check", "Not all cells are filled yet.")
            return
        # Verify all rows/cols/regions
        ok = True
        for i in range(9):
            row = set(self.puzzle[i])
            if row != set(range(1,10)):
                ok = False
                break
        for j in range(9):
            col = set(self.puzzle[i][j] for i in range(9))
            if col != set(range(1,10)):
                ok = False
                break
        for br in (0,3,6):
            for bc in (0,3,6):
                s = set()
                for i in range(br,br+3):
                    for j in range(bc,bc+3):
                        s.add(self.puzzle[i][j])
                if s != set(range(1,10)):
                    ok = False
                    break
        if ok:
            messagebox.showinfo("Result", "Congratulations! Puzzle is correct.")
        else:
            messagebox.showinfo("Result", "Puzzle is complete but has errors.")

if __name__ == '__main__':
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()
