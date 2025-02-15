"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


class OutOfBoundsError(Exception):
    """Personalizated exception for players out of bound"""
    pass


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def total_filled_cells(board):
    """
    Returns the total of filled cells on the board
    """

    # This variable storages the total filled cells on the board
    total = 0

    # Loop to traverse the matriz
    for i in board:
        for j in i:
            if j is not None:
                total += 1

    return total


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    
    # Once X gets the first move, if the board has even filled cells, the X playr plays, else, the O player plays
    if total_filled_cells(board) % 2 == 0:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    set_of_actions = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                action = (i, j)
                set_of_actions.add(action)
    
    return set_of_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = copy.deepcopy(board)

    if action[0] < 0 or action[0] >= len(board) or action[1] < 0 or action[1] >= len(board[0]):
        raise OutOfBoundsError("This position isn't available.")

    if new_board[action[0]][action[1]] is not None:
        raise OutOfBoundsError("This position isn't available.")

    given_player = player(board)
    new_board[action[0]][action[1]] = given_player
        
    return new_board


def check_player_win_by_row(board, player):
    for i in board:
        if i == [player, player, player]:
            return True
    return False
        

def check_player_win_by_collunms(board, player):
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] == player:
            return True
    return False


def check_player_win_by_diagonals(board, player):
    if board[0][0] == board[1][1] == board[2][2] == player:
        return True
    if board[0][2] == board[1][1] == board[2][0] == player:
        return True
    return False


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if check_player_win_by_row(board, X) or check_player_win_by_collunms(board, X) or check_player_win_by_diagonals(board, X):
        return X
    elif check_player_win_by_row(board, O) or check_player_win_by_collunms(board, O) or check_player_win_by_diagonals(board, O):
        return O
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None or total_filled_cells(board) == 9:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def max_value(board, alpha=float('-inf'), beta=float('inf')):
    if terminal(board):
        return utility(board)

    value = float('-inf')
    for action in actions(board):
        value = max(value, min_value(result(board, action), alpha, beta))
        if value >= beta:
            return value  
        alpha = max(alpha, value)
    return value


def min_value(board, alpha=float('-inf'), beta=float('inf')):
    if terminal(board):
        return utility(board)

    value = float('inf')
    for action in actions(board):
        value = min(value, max_value(result(board, action), alpha, beta))
        if value <= alpha:
            return value
        beta = min(beta, value)
    return value


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    if player(board) == "X":
        best_value = -2
        best_action = None
        for action in actions(board):
            value = min_value(result(board, action))
            if value > best_value:
                best_value = value
                best_action = action

    else:
        best_value = 2
        best_action = None
        for action in actions(board):
            value = max_value(result(board, action))
            if value < best_value:
                best_value = value
                best_action = action

    return best_action