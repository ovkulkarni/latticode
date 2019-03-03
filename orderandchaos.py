import latticode

game = latticode.Game('Order & Chaos')
brd = game.create_board(7, 7)
game.create_players('order', 'chaos')

game.create_piece('Blue', sprite='Blue')
game.create_piece('Red', sprite='Red')

game.set_initial_state(latticode.EMPTY_BOARD)
game.add_sidelined_piece('Red', count=latticode.INFINITY)
game.add_sidelined_piece('Blue', count=latticode.INFINITY)


def legal_moves(piece, piece_loc, board):
    if piece_loc is None:
        return latticode.to_moves(board.open_spaces())
    return []


def make_move(piece, piece_loc, move, board):
    new_board = board.copy()
    new_board[move.loc] = piece
    new_board.current_player = 'order' if new_board.current_player == 'chaos' else 'chaos'
    return new_board


def check_status(game, board):
    order_possible = False
    for piece in game.pieces:
        if board.in_line(5, piece):
            return "order"
        temp_board = board.copy()
        temp_board.board = [[piece if p is None else p for p in row]
                            for row in temp_board.board]
        if temp_board.in_line(5, piece):
            order_possible = True
    if not order_possible:
        return "chaos"
    return latticode.ONGOING


game.set_initial_player('order')
game.set_legal_moves_function(legal_moves)
game.set_make_move_function(make_move)
game.set_check_status_function(check_status)
