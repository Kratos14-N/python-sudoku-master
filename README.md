# Python Sudoku Master

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![GUI](https://img.shields.io/badge/GUI-Tkinter-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

A complete Sudoku game with a graphical interface, three difficulty levels, pencil notes, mistake tracking, a timer, and an automatic solver.

## Features

- Randomly generated, valid Sudoku puzzles
- Easy, Medium, and Hard difficulty levels
- Guaranteed single-solution puzzle generation
- Interactive 9x9 Tkinter board
- Pencil mode for candidate notes
- Timer and three-mistake limit
- Erase control and keyboard input
- Built-in automatic solver
- Win and game-over notifications

## Requirements

- Python 3.8 or newer
- Tkinter

Tkinter is included with the standard Python installer on Windows and macOS. On some Linux distributions, install it using your package manager (for example, `sudo apt install python3-tk`).

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/Kratos14-N/python-sudoku-master.git
cd python-sudoku-master
```

No third-party Python packages are required.

## Run the Game

```bash
python sudoku.py
```

On macOS or Linux, use `python3 sudoku.py` if `python` is not available.

## How to Play

1. Select a cell with the mouse.
2. Enter a number from 1 to 9 using the keyboard.
3. Use the pencil button to add or remove candidate notes.
4. Use **Erase** or the Delete/Backspace key to clear an editable cell.
5. Choose a difficulty to start a new puzzle.
6. Click **Auto-Solve** to complete the board.

Incorrect entries count toward the three-mistake limit. Fixed puzzle values cannot be changed.

## Project Structure

```text
python-sudoku-master/
├── sudoku.py
├── README.md
├── LICENSE
└── .gitignore
```

## Technical Overview

- `SudokuEngine` validates placements, solves boards, counts solutions, and generates puzzles.
- Puzzle generation creates a complete randomized board and removes clues while preserving exactly one solution.
- `SudokuGUI` manages the Tkinter window, board rendering, timer, notes, input, and game state.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
