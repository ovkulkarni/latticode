import latticode

game = latticode.Game('Ultimae Tic-Tac-Toe')


def build_quasiboard(state):
    board = latticode.Board(len(state[0]), len(state), game)
    board.board = state
    return board


brd = game.create_board(9, 9,
                        next_region=None,
                        unwon_regions={(a, b) for a in range(3)
                                       for b in range(3)},
                        region_wins=[[None] * 3, [None] * 3, [None] * 3])
game.create_players('X', 'O')

game.create_piece('X', sprite='x')
game.create_piece('O', sprite='o')

game.add_sidelined_piece('X', count=latticode.INFINITY)
game.add_sidelined_piece('O', count=latticode.INFINITY)
game.set_initial_state(latticode.EMPTY_BOARD)


def region_of(loc): return (loc[0] // 3, loc[1] // 3)


def subregion_of(loc): return (loc[0] % 3, loc[1] % 3)


def build_region_board(board, region):
    r_state = [[board[y, x] for x in range(region[1] * 3, region[1] * 3 + 3)]
               for y in range(region[0] * 3, region[0] * 3 + 3)]
    return build_quasiboard(r_state)


def legal_moves(piece, piece_loc, board):
    if piece == board.current_player and piece_loc is None:
        regions = [
            board.next_region] if board.next_region is not None else board.unwon_regions
        return latticode.to_moves(
            [loc for loc in board.open_spaces() if region_of(loc) in regions])
    return []


def make_move(piece, piece_loc, move, board):
    new_board = board.copy()
    new_board[move.loc] = piece
    region, subregion = region_of(move.loc), subregion_of(move.loc)
    rboard = build_region_board(new_board, region)
    if rboard.in_line(3, board.current_player):
        new_board.unwon_regions.remove(region)
        new_board.region_wins[region[0]][region[1]] = board.current_player
    new_board.next_region = subregion if subregion in new_board.unwon_regions else None
    new_board.current_player = 'X' if new_board.current_player == 'O' else 'O'
    return new_board


def check_status(game, board):
    quasi = build_quasiboard(board.region_wins)
    for player in game.players:
        if quasi.in_line(3, player):
            return player
    if quasi.all_filled():
        return latticode.TIE
    return latticode.ONGOING


game.set_initial_player('X')
game.set_legal_moves_function(legal_moves)
game.set_make_move_function(make_move)
game.set_check_status_function(check_status)
