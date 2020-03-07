#!/usr/bin/env python
import tkinter as tk
import re
import copy
import time
from timer import time_function, get_clock, start_named_timer, stop_named_timer

import threading
import numpy as np

EMPTY = "."
WALL = "#"


class Drawer:
    def __init__(self, shape, sq_size=40):
        self.master = tk.Tk()
        self.shape = shape
        self.sq_size = sq_size
        self.width = self.shape[0] * self.sq_size + 2
        self.height = self.shape[1] * self.sq_size + 2
        self.canvas = tk.Canvas(self.master, width=self.width, height=self.height)
        self.canvas.pack()

    def idx2coord(self, x, y):
        return ((x + 0.5) * self.sq_size, (y + 0.5) * self.sq_size)

    def draw_board(self, board):
        for idx, val in np.ndenumerate(board):
            x, y = self.idx2coord(idx[0], idx[1])
            if val == WALL:
                self.canvas.create_rectangle(
                    x, y, x + self.sq_size, y + self.sq_size, fill="black"
                )
            else:
                self.canvas.create_rectangle(
                    x, y, x + self.sq_size, y + self.sq_size, fill="white"
                )
                if val.isnumeric():
                    self.canvas.create_text(
                        x + self.sq_size / 4, y + self.sq_size / 4, text=val
                    )


def main():
    across = [
        1,
        6,
        10,
        12,
        13,
        14,
        16,
        17,
        19,
        20,
        21,
        23,
        25,
        27,
        29,
        30,
        31,
        33,
        34,
        35,
        37,
        38,
        40,
        41,
        42,
        44,
        45,
        46,
        49,
        50,
    ]
    down = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        15,
        17,
        18,
        20,
        21,
        22,
        24,
        26,
        28,
        32,
        33,
        36,
        39,
        41,
        43,
        45,
        47,
        48,
    ]
    across = [str(i) for i in across]
    down = [str(i) for i in down]
    # segments = get_segments(across, down)
    draw = Drawer((17, 17))
    # solver = get_solver(15, 15, across, down, draw)
    solver = get_solver_new(15, 15, across, down, draw)
    threading.Thread(target=solver).start()
    tk.mainloop()


def valid_placement(board, n, size, x, y, across, down):
    if n in across and size - x < 2 or n in down and size - y < 2:
        return False
    if n == EMPTY and (y == 0 or board[x][y - 1] == WALL):
        return False
    return True


@time_function
def place_segment(board, x, y, segment, across, down, length):
    x_orig = x
    to_place = list(segment) + [EMPTY] * (3 - len(segment))
    if valid_placement(board, segment[0], length, x, y, across, down):
        board[x][y] = segment[0]
        i = 1
    else:
        return False
    for x in range(x_orig + 1, length):
        if y == 0 or board[x][y - 1] == WALL:
            if i >= len(to_place):
                print(to_place, i, x, x_orig, segment)
            if valid_placement(board, to_place[i], length, x, y, across, down):
                board[x][y] = to_place[i]
                i += 1
            else:
                return False
        else:
            board[x][y] = EMPTY
        if i >= len(segment) and x - x_orig >= 2:
            return x + 1
    return False


def get_segments(across, down):
    highest = int(max(across + down, key=lambda n: int(n)))
    segments = []
    segment = []
    for n in range(1, highest + 1):
        if str(n) in across and segment:
            segments.append(segment)
            segment = []
        segment.append(str(n))
    segments.append(segment)
    return segments


def get_solver(size_x, size_y, across, down, draw):
    def solve_crossword():
        board = [[""] * (size_x + 2) for _ in range(size_y + 2)]
        if solve_crossword_util_num(board, 0, 0, 1, across, down, draw):
            print_board(board)
        else:
            print("No solution found!")

    return solve_crossword


def get_solver_new(size_x, size_y, across, down, draw):
    def solve_crossword():
        board = [[""] * (size_x) for _ in range(size_y)]
        segments = get_segments(across, down)
        start_named_timer("Full")
        length = len(board)
        if solve_crossword_util(board, 0, 0, segments, 0, across, down, draw, length):
            print_board(board)
        else:
            stop_named_timer("Full", total=False)
            clock = get_clock()
            print(f"No solution found! {clock}")
            print(
                f"{clock['Full'][1] / clock['get_candidates_new'][0]}s per get_candidates_new call"
            )

    return solve_crossword


@time_function
def fill_with_walls(board, x, y, down, length):
    for x2 in range(x, length):
        for y2 in range(y - 2, y):
            if board[x2][y2] in down:
                return False
        board[x2][y] = WALL
    return x2 + 1


def solve_crossword_util(board, x, y, segments, segi, across, down, draw, length):
    clock = get_clock()
    if "total" in clock and clock["total"][1] > 120:
        return False
    if "total" in clock and not clock["total"][0] % 80000:
        print_board(board, draw, y_max=y, x_max=x)
    if y > length - 3 and max(down) >= segments[segi][0]:
        return False

    next_num = segments[segi][0]
    moves = get_candidates_new(
        board, x, y, across, down, str(next_num), len(segments[segi]), length
    )
    if not moves:
        return False
    if y == x == length - 1:
        if next_num == max(across + down, key=lambda n: int(n)):
            return True
        else:
            return False

    if str(next_num) in moves:
        if x2 := place_segment(board, x, y, segments[segi], across, down, length):
            n = y * length + x2
            x2 = n % length
            y2 = n // length
            solved = solve_crossword_util(
                board, x2, y2, segments, segi + 1, across, down, draw, length
            )
            if solved:
                return True
        elif x2 := fill_with_walls(board, x, y, down, length):
            n = y * length + x2
            x2 = n % length
            y2 = n // length
            solved = solve_crossword_util(
                board, x2, y2, segments, segi, across, down, draw, length
            )
            if solved:
                return True
        else:
            return False

    n = y * length + x + 1
    x2 = n % length
    y2 = n // length

    if WALL in moves:
        board[x][y] = WALL
        solved = solve_crossword_util(
            board, x2, y2, segments, segi, across, down, draw, length
        )
        if solved:
            return True
    if EMPTY in moves:
        board[x][y] = EMPTY
        solved = solve_crossword_util(
            board, x2, y2, segments, segi, across, down, draw, length
        )
        if solved:
            return True
    return False


@time_function
def get_candidates_new(board, x, y, across, down, next_num, seg_size, length):
    candidates = {EMPTY, WALL, next_num}

    if x != 0 and board[x - 1][y] != WALL:
        if y == 0 or board[x][y - 1] == WALL:
            candidates &= {WALL}
        else:
            candidates -= {next_num}
    elif y != 0 and board[x][y - 1] != WALL:
        if next_num in down:
            candidates &= {WALL}

    if x == 0 or board[x - 1][y] == WALL or y == 0 or board[x][y - 1] == WALL:
        candidates -= {EMPTY}

    if length - x <= max(2, seg_size):
        candidates -= {next_num}

    if (next_num in down or seg_size >= 2) and length - y <= 2:
        candidates -= {next_num}

    # Shortest word is three letters
    for y2 in range(y - 2, y):
        if y2 >= 0 and board[x][y2] in down:
            candidates -= {WALL}
            break

    return candidates


# def print_board(board, x_max=-1, y_max=-1):
#     space_left = len(board) - x - len(segments[segi])
#     if space_left < 0:
#         return set()
#     elif not space_left:
#         return {segments[segi]}
#     else:
#         return {WALLments[segi]}


def solve_crossword_util_num(board, x, y, next_num, across, down, draw):
    print_board(board, draw, y_max=y, x_max=x)
    moves = get_candidates(board, x, y, across, down, str(next_num))
    if not moves:
        return False
    if y == x == len(board) - 1:
        if next_num == max(across + down, key=lambda n: int(n)) + 1:
            return True
        else:
            return False

    n = y * len(board[y]) + x + 1
    x2 = n % len(board[y])
    y2 = n // len(board)

    if str(next_num) in moves:
        board[x][y] = str(next_num)
        solved = solve_crossword_util_num(
            board, x2, y2, next_num + 1, across, down, draw
        )
        if solved:
            return True

    for move in moves - {str(next_num)}:
        board[x][y] = move
        solved = solve_crossword_util_num(board, x2, y2, next_num, across, down, draw)
        if solved:
            return True
    return False


def get_candidates(board, x, y, across, down, next_num):
    candidates = {EMPTY, WALL, next_num}
    # Board is padded with walls to make logic simpler
    if x == 0 or y == 0:
        return {WALL}
    if x == len(board[y]) - 1 or y == len(board) - 1:
        candidates &= {WALL}

    # If the cell above is a wall the cell has either a number or a wall in it.
    # If the cell to the left is not a wall but the next number should be across
    # it have to be a wall
    if board[x][y - 1] == WALL and board[x - 1][y] != WALL and next_num in across:
        candidates &= {WALL}
    # Same logic but for down
    if board[x - 1][y] == WALL and board[x][y - 1] != WALL and next_num in down:
        candidates &= {WALL}

    if next_num in across and len(board) - x <= 3:
        candidates -= {next_num}

    if next_num in down and len(board) - y <= 3:
        candidates -= {next_num}
    # Shortest word is three letters
    for x2 in range(x - 2, x):
        if x2 >= 0 and board[x2][y] in across:
            candidates -= {WALL}
            break
    for y2 in range(y - 2, y):
        if y2 >= 0 and board[x][y2] in down:
            candidates -= {WALL}
            break

    # If a cell contains a wall then the next number will have to be in across
    if next_num not in across:
        candidates -= {WALL}

    if board[x - 1][y] == WALL or board[x][y - 1] == WALL:
        candidates -= {EMPTY}
    else:
        candidates -= {next_num}

    return candidates


@time_function
def print_board(board, draw, x_max=-1, y_max=-1):
    if x_max != -1 and y_max != -1:
        board = copy.deepcopy(board)
        latest = False
        for y in range(len(board)):
            for x in range(len(board)):
                if y == y_max and x == x_max:
                    latest = True
                if latest:
                    board[x][y] = "."
    # start_named_timer("draw")
    draw.draw_board(board)
    # stop_named_timer("draw", total=False)


if __name__ == "__main__":
    main()
