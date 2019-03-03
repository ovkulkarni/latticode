import latticode

ttt = latticode.Game('Connect 4')
brd = ttt.create_board(7, 6)
ttt.create_players('blue', 'Red')

ttt.create_piece('blue', sprite='X')
ttt.create_piece('Red', sprite='O')

ttt.set_initial_state(latticode.EMPTY_BOARD)
ttt.add_sidelined_piece('blue', count=latticode.INFINITY)
ttt.add_sidelined_piece('Red', count=latticode.INFINITY)


def legal_moves(piece, piece_loc, board):
    if piece == board.current_player and piece_loc is None:
        return latticode.to_moves(board.open_spaces_gravity())
    return []


def make_move(piece, piece_loc, move, board):
    new_board = board.copy()
    new_board[move.loc] = piece
    new_board.current_player = 'blue' if new_board.current_player == 'Red' else 'Red'
    return new_board


def check_status(game, board):
    for player in game.players:
        if board.in_line(4, player):
            return player
    if board.all_filled():
        return latticode.TIE
    return latticode.ONGOING


ttt.set_initial_player('blue')
ttt.set_legal_moves_function(legal_moves)
ttt.set_make_move_function(make_move)
ttt.set_check_status_function(check_status)

game = ttt