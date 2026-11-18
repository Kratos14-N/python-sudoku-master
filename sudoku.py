import random
import time
import tkinter as tk
from tkinter import messagebox


class SudokuEngine:
    @staticmethod
    def is_valid(grid, row, col, num):
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        return not (
            num in grid[row]
            or any(grid[r][col] == num for r in range(9))
            or any(
                grid[r][c] == num
                for r in range(box_row, box_row + 3)
                for c in range(box_col, box_col + 3)
            )
        )

    @staticmethod
    def find_empty(grid):
        return next(
            ((r, c) for r in range(9) for c in range(9) if grid[r][c] == 0),
            None,
        )

    @classmethod
    def solve(cls, grid):
        empty = cls.find_empty(grid)
        if empty is None:
            return True
        row, col = empty
        for num in range(1, 10):
            if cls.is_valid(grid, row, col, num):
                grid[row][col] = num
                if cls.solve(grid):
                    return True
                grid[row][col] = 0
        return False

    @classmethod
    def count_solutions(cls, grid, limit=2):
        empty = cls.find_empty(grid)
        if empty is None:
            return 1
        row, col = empty
        count = 0
        for num in range(1, 10):
            if cls.is_valid(grid, row, col, num):
                grid[row][col] = num
                count += cls.count_solutions(grid, limit)
                grid[row][col] = 0
                if count >= limit:
                    break
        return count

    @classmethod
    def generate_full_board(cls):
        grid = [[0] * 9 for _ in range(9)]
        def fill():
            empty = cls.find_empty(grid)
            if empty is None:
                return True
            row, col = empty
            numbers = list(range(1, 10))
            random.shuffle(numbers)
            for num in numbers:
                if cls.is_valid(grid, row, col, num):
                    grid[row][col] = num
                    if fill():
                        return True
                    grid[row][col] = 0
            return False
        fill()
        return grid

    @classmethod
    def generate_puzzle(cls, difficulty="Medium"):
        full_board = cls.generate_full_board()
        solution = [row[:] for row in full_board]
        puzzle = [row[:] for row in full_board]
        removals_needed = 81 - {"Easy": 36, "Medium": 30, "Hard": 24}.get(difficulty, 30)
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        removed = 0
        for r, c in cells:
            if removed >= removals_needed:
                break
            value = puzzle[r][c]
            puzzle[r][c] = 0
            if cls.count_solutions([row[:] for row in puzzle]) != 1:
                puzzle[r][c] = value
            else:
                removed += 1
        return puzzle, solution


class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Sudoku Master")
        self.root.geometry("560x720")
        self.root.resizable(False, False)
        self.root.configure(bg="#F4F6F9")

        self.difficulty = "Medium"
        self.puzzle = []
        self.initial_puzzle = []
        self.solution = []
        self.selected_cell = None
        self.notes = {}
        self.note_mode = False
        self.mistakes = 0
        self.max_mistakes = 3
        self.game_over = False

        self.start_time = None
        self.timer_running = False

        self._init_ui()
        self.new_game("Medium")

    def _init_ui(self):
        stats_frame = tk.Frame(self.root, bg="#F4F6F9")
        stats_frame.pack(fill=tk.X, padx=20, pady=(15, 5))

        label_style = {"font": ("Helvetica", 11, "bold"), "bg": "#F4F6F9", "fg": "#2C3E50"}
        self.lbl_difficulty = tk.Label(stats_frame, text="Difficulty: Medium", **label_style)
        self.lbl_difficulty.pack(side=tk.LEFT)
        self.lbl_mistakes = tk.Label(stats_frame, text="Mistakes: 0/3", fg="#E74C3C", **{k: v for k, v in label_style.items() if k != "fg"})
        self.lbl_mistakes.pack(side=tk.LEFT, padx=30)
        self.lbl_timer = tk.Label(stats_frame, text="Time: 00:00", **label_style)
        self.lbl_timer.pack(side=tk.RIGHT)

        self.cell_size = 54
        self.margin = 15
        self.canvas_size = self.cell_size * 9 + self.margin * 2

        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size,
                                bg="white", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.root.bind("<Key>", self._on_key_press)
        ctrl_frame = tk.Frame(self.root, bg="#F4F6F9")
        ctrl_frame.pack(fill=tk.X, padx=20, pady=5)

        button_style = {"font": ("Helvetica", 10, "bold"), "relief": tk.FLAT, "padx": 10, "pady": 5}
        self.btn_note = tk.Button(ctrl_frame, text="✏️ Pencil: OFF", bg="#BDC3C7",
                                  fg="#2C3E50", command=self.toggle_note_mode, **button_style)
        self.btn_note.pack(side=tk.LEFT, padx=5)
        btn_erase = tk.Button(ctrl_frame, text="⌫ Erase", bg="#BDC3C7", fg="#2C3E50",
                              command=self.erase_current_cell, **button_style)
        btn_erase.pack(side=tk.LEFT, padx=5)
        btn_solve = tk.Button(ctrl_frame, text="🤖 Auto-Solve", bg="#9B59B6", fg="white",
                              command=self.auto_solve, **button_style)
        btn_solve.pack(side=tk.RIGHT, padx=5)

        bottom_frame = tk.Frame(self.root, bg="#F4F6F9")
        bottom_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(bottom_frame, text="New:", font=("Helvetica", 10, "bold"), bg="#F4F6F9").pack(side=tk.LEFT)
        for diff in ["Easy", "Medium", "Hard"]:
            btn = tk.Button(bottom_frame, text=diff, font=("Helvetica", 9), bg="#3498DB",
                            fg="white", relief=tk.FLAT, padx=8, pady=3,
                            command=lambda d=diff: self.new_game(d))
            btn.pack(side=tk.LEFT, padx=4)

    def new_game(self, difficulty="Medium"):
        self.difficulty = difficulty
        self.lbl_difficulty.config(text=f"Difficulty: {difficulty}")
        self.puzzle, self.solution = SudokuEngine.generate_puzzle(difficulty)
        self.initial_puzzle = [row[:] for row in self.puzzle]
        self.selected_cell = None
        self.notes.clear()
        self.mistakes = 0
        self.game_over = False
        self.lbl_mistakes.config(text="Mistakes: 0/3")

        self.start_time = time.time()
        self.timer_running = True
        self._update_timer()
        self.draw_board()

    def _update_timer(self):
        if self.timer_running and not self.game_over:
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            self.lbl_timer.config(text=f"Time: {mins:02d}:{secs:02d}")
            self.root.after(1000, self._update_timer)

    def toggle_note_mode(self):
        self.note_mode = not self.note_mode
        if self.note_mode:
            self.btn_note.config(text="✏️ Pencil: ON", bg="#2ECC71", fg="white")
        else:
            self.btn_note.config(text="✏️ Pencil: OFF", bg="#BDC3C7", fg="#2C3E50")

    def draw_board(self):
        self.canvas.delete("all")

        if self.selected_cell:
            sel_r, sel_c = self.selected_cell
            for i in range(9):
                self._highlight_cell(sel_r, i, "#EBF5FB")
                self._highlight_cell(i, sel_c, "#EBF5FB")
            self._highlight_cell(sel_r, sel_c, "#AED6F1")

        for i in range(10):
            width = 3 if i % 3 == 0 else 1
            color = "#2C3E50" if i % 3 == 0 else "#BDC3C7"
            x = self.margin + i * self.cell_size
            self.canvas.create_line(x, self.margin, x, self.margin + 9 * self.cell_size, width=width, fill=color)
            y = self.margin + i * self.cell_size
            self.canvas.create_line(self.margin, y, self.margin + 9 * self.cell_size, y, width=width, fill=color)

        for r in range(9):
            for c in range(9):
                val = self.puzzle[r][c]
                cx = self.margin + c * self.cell_size + self.cell_size // 2
                cy = self.margin + r * self.cell_size + self.cell_size // 2
                if val != 0:
                    color = "#2C3E50" if self.initial_puzzle[r][c] != 0 else "#2980B9"
                    font = ("Helvetica", 18, "bold") if self.initial_puzzle[r][c] != 0 else ("Helvetica", 18)
                    self.canvas.create_text(cx, cy, text=str(val), font=font, fill=color)
                elif self.notes.get((r, c)):
                    for note in self.notes[(r, c)]:
                        nr = (note - 1) // 3
                        nc = (note - 1) % 3
                        nx = self.margin + c * self.cell_size + 12 + nc * 15
                        ny = self.margin + r * self.cell_size + 12 + nr * 15
                        self.canvas.create_text(nx, ny, text=str(note), font=("Helvetica", 8), fill="#7F8C8D")

    def _highlight_cell(self, r, c, color):
        x1 = self.margin + c * self.cell_size
        y1 = self.margin + r * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def _on_canvas_click(self, event):
        if self.game_over:
            return
        x, y = event.x - self.margin, event.y - self.margin
        if 0 <= x < 9 * self.cell_size and 0 <= y < 9 * self.cell_size:
            c = int(x // self.cell_size)
            r = int(y // self.cell_size)
            self.selected_cell = (r, c)
            self.draw_board()

    def _on_key_press(self, event):
        if self.game_over or not self.selected_cell:
            return

        r, c = self.selected_cell

        if self.initial_puzzle[r][c] != 0:
            return

        if event.char in "123456789":
            val = int(event.char)
            if self.note_mode:
                notes = self.notes.setdefault((r, c), set())
                notes.symmetric_difference_update({val})
                self.draw_board()
            else:
                if val == self.solution[r][c]:
                    self.puzzle[r][c] = val
                    self.notes.pop((r, c), None)
                    self.draw_board()
                    self._check_win()
                else:
                    self.mistakes += 1
                    self.lbl_mistakes.config(text=f"Mistakes: {self.mistakes}/{self.max_mistakes}")
                    if self.mistakes >= self.max_mistakes:
                        self.game_over = True
                        messagebox.showerror("Game Over", "You reached 3 mistakes! Try again.")
                    else:
                        messagebox.showwarning("Incorrect", f"{val} is not correct here.")

        elif event.keysym in ("BackSpace", "Delete"):
            self.erase_current_cell()

    def erase_current_cell(self):
        if not self.selected_cell or self.game_over:
            return
        r, c = self.selected_cell
        if self.initial_puzzle[r][c] == 0:
            self.puzzle[r][c] = 0
            self.notes.pop((r, c), None)
            self.draw_board()

    def auto_solve(self):
        if self.game_over:
            return
        self.puzzle = [row[:] for row in self.solution]
        self.game_over = True
        self.timer_running = False
        self.draw_board()
        messagebox.showinfo("Solved", "The board has been completed!")

    def _check_win(self):
        if any(self.puzzle[r][c] != self.solution[r][c] for r in range(9) for c in range(9)):
            return
        self.game_over = True
        self.timer_running = False
        messagebox.showinfo("Congratulations!", f"You solved the puzzle in {self.lbl_timer.cget('text').split()[1]}!")


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()