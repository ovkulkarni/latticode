import latticode

ttt = latticode.Game('Tic Tac Two')
brd = ttt.create_board(3, 3)
ttt.create_players('X', 'O')

ttt.create_piece('X', sprite='X')
ttt.create_piece('O', sprite='O')

ttt.set_initial_state(latticode.EMPTY_BOARD)
ttt.add_sidelined_piece('X', count=latticode.INFINITY)
ttt.add_sidelined_piece('O', count=latticode.INFINITY)


def legal_moves(piece, piece_loc, board):
    if piece == board.current_player and piece_loc is None:
        return board.open_spaces()
    return []


def make_move(piece, piece_loc, move, board):
    new_board = board.copy()
    new_board[move] = piece
    new_board.current_player = 'X' if new_board.current_player == 'O' else 'O'
    return new_board


def check_win(board, player):
    if board.in_row(length=3, piece=player):
        return True
    if board.in_col(length=3, piece=player):
        return True
    elif board.in_diag(length=3, piece=player):
        return True
    return False


ttt.set_initial_player('X')
ttt.set_legal_moves_function(legal_moves)
ttt.set_make_move_function(make_move)
ttt.set_check_win_function(check_win)

game = ttt

# print(ttt.board)
# for p in ttt.board.sidelined_pieces:
#     print(p, ttt.legal_moves_func(p, None))

# ttt.make_move_func('X', None, (0, 0))
# print(ttt.board)

# for p in ttt.board.sidelined_pieces:
#     print(p, ttt.legal_moves_func(p, None))

# ttt.make_move_func('X', None, (1, 1))
# ttt.make_move_func('X', None, (2, 2))
# print(ttt.board)

# print(ttt.check_win_func('X'))
# print(ttt.past)
