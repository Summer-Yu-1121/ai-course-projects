import sudoku_logic

CURRENT = {
    "puzzle": None,
    "solution": None,
}


def create_new_game(difficulty):
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty)
    CURRENT["puzzle"] = sudoku_logic.deep_copy(puzzle)
    CURRENT["solution"] = sudoku_logic.deep_copy(solution)
    return puzzle


def check_solution(board):
    solution = CURRENT.get("solution")
    if solution is None:
        return None, "No game in progress"

    incorrect = []
    incomplete = False

    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] == 0:
                incomplete = True
            elif board[i][j] != solution[i][j]:
                incorrect.append([i, j])

    if incomplete:
        return incorrect, "Puzzle is not complete"

    return incorrect, None


def get_hint():
    puzzle = CURRENT.get("puzzle")
    solution = CURRENT.get("solution")

    if puzzle is None or solution is None:
        return None, "No game in progress"

    for i in range(len(puzzle)):
        for j in range(len(puzzle[i])):
            if puzzle[i][j] == 0:
                value = solution[i][j]
                puzzle[i][j] = value
                return {"row": i, "col": j, "value": value}, None

    return None, "No empty cells available"