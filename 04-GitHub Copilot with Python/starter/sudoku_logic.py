import copy
import random

SIZE = 9
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False

    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False

    return True


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)

                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY

                return False
    return True


def count_solutions(board, limit=2):
    """
    Count the number of solutions for a Sudoku board.
    Stops early if the number of solutions reaches the limit.
    """
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                count = 0
                for num in range(1, SIZE + 1):
                    if is_safe(board, row, col, num):
                        board[row][col] = num
                        count += count_solutions(board, limit)
                        if count >= limit:
                            board[row][col] = EMPTY
                            return limit
                        board[row][col] = EMPTY
                return count
    return 1


def remove_cells(board, clues):
    cells_to_remove = SIZE * SIZE - clues
    attempts = 0

    # Try more attempts to ensure uniqueness, especially for hard puzzles
    while cells_to_remove > 0 and attempts < SIZE * SIZE * 4:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)

        if board[row][col] == EMPTY:
            attempts += 1
            continue

        backup = board[row][col]
        board[row][col] = EMPTY

        board_copy = deep_copy(board)
        solutions = count_solutions(board_copy, limit=2)

        if solutions != 1:
            board[row][col] = backup
            attempts += 1
        else:
            cells_to_remove -= 1


def has_unique_solution(board):
    return count_solutions(deep_copy(board), limit=2) == 1

def generate_puzzle(difficulty):
    clues = {"easy": 45, "medium": 35, "hard": 25}[difficulty]
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    while not has_unique_solution(deep_copy(board)):
        board = create_empty_board()
        fill_board(board)
        remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution