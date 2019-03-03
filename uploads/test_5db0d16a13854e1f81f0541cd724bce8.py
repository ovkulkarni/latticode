def legal_moves(piece, board, player):
    if piece.name == player.name:
        return board.open_spaces()
    return []


def make_move(move, piece, board, player):
    board[move] = piece
    return 'X' if player == 'O' else 'O'


def check_win(board, player):
    if board.in_row(length=3, piece=player.name):
        return True
    if board.in_col(length=3, piece=player.name):
        return True
    elif board.in_diag(length=3, piece=player.name):
        return True
    return False


ttt.set_initial_player('X')
ttt.set_legal_moves_function(legal_moves)
ttt.set_make_move_function(make_move)
ttt.set_check_win_function(check_win)

"""
print(ttt.board)
for p in ttt.board.sidelined_pieces:
    piece = ttt.get_piece(p)
    print(p, ttt.legal_moves_func(piece))

piece = ttt.get_piece('X')
ttt.make_move_func((0, 0), piece)
print(ttt.board)

for p in ttt.board.sidelined_pieces:
    piece = ttt.get_piece(p)
    print(p, ttt.legal_moves_func(piece))

piece = ttt.get_piece('X')
ttt.make_move_func((1, 1), piece)
ttt.make_move_func((2, 2), piece)
print(ttt.board)

print(ttt.check_win_func(ttt.get_player('O')))
print(ttt.board.past)
"""
