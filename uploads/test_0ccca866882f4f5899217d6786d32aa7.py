import latticode

ttt = latticode.Game('Tic Tac Toe')
brd = ttt.create_board(3, 3)
ttt.create_players('X', 'O')

ttt.create_piece('X', sprite='X')
ttt.create_piece('O', sprite='O') 

ttt.set_initial_state([['X', 'O', None], [None, None, None], [None, None, None]])
ttt.add_sidelined_piece('X', count=latticode.INFINITY)
ttt.add_sidelined_piece('O', count=latticode.INFINITY)


def legal_moves(piece, piece_loc, board):
    if piece == board.current_player and piece_loc is None:
        return latticode.to_moves(board.open_spaces())
    return []


def make_move(piece, piece_loc, move, board):
    new_board = board.copy()
    new_board[move.loc] = piece
    new_board.current_player = 'X' if new_board.current_player == 'O' else 'O'
    return new_board


def check_status(game, board):
    for player in game.players:
        if board.in_line(3, player):
            return player
    if board.all_filled():
        return latticode.TIE
    return latticode.ONGOING


ttt.set_initial_player('X')
ttt.set_legal_moves_function(legal_moves)
ttt.set_make_move_function(make_move)
ttt.set_check_status_function(check_status)

game = ttt