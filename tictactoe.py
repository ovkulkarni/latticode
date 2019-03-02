import game

ttt = game.Game('Tic Tac Toe')
brd = ttt.create_board(3, 3)
ttt.create_players('X', 'O')
ttt.create_piece('X', sprite='X')
ttt.create_piece('O', sprite='O')

brd.initial_state(game.EMPTY_BOARD)
brd.add_sidelined_piece('X', count=game.INFINITY)
brd.add_sidelined_piece('O', count=game.INFINITY)


def legal_moves(piece, board, player):
    if piece.name == player.name:
        return board.open_spaces()
    return []


def make_move(move, piece, board, player):
    board[move] = piece


def check_win(board, player):
    return board.in_row(length=3, piece=player.name)


ttt.set_legal_moves_function(legal_moves)
ttt.set_make_moves_function(make_move)
ttt.set_check_win_function(check_win)
