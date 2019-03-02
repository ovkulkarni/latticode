import game

ttt = game.Game('Tic Tac Toe')
brd = ttt.create_board(3, 3)
ttt.create_players('X', 'O')

ttt.create_piece('X', sprite='X')
ttt.create_piece('O', sprite='O')

brd.set_initial_state(game.EMPTY_BOARD)
brd.add_sidelined_piece('X', count=game.INFINITY)
brd.add_sidelined_piece('O', count=game.INFINITY)


def legal_moves(piece, board, player):
    if piece.name == player.name:
        return board.open_spaces()
    return []


def make_move(move, piece, board, player):
    board[move] = piece


make_move((1, 1), ttt.get_piece('X')(), brd, ttt.get_player('X'))
make_move((0, 0), ttt.get_piece('X')(), brd, ttt.get_player('X'))
make_move((2, 2), ttt.get_piece('X')(), brd, ttt.get_player('X'))
print(brd)
# print(legal_moves(ttt.get_piece('X')(), brd, ttt.get_player('X')))


def check_win(board, player):
    if board.in_row(length=3, piece=player.name):
        return True
    elif board.in_col(length=3, piece=player.name):
        return True
    elif board.in_diag(length=3, piece=player.name):
        return True
    return False

# ttt.set_legal_moves_function(legal_moves)
# ttt.set_make_moves_function(make_move)
# ttt.set_check_win_function(check_win)
