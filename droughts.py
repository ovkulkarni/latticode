import latticode
from collections import defaultdict

droughts = latticode.Game('Droughts')
brd = droughts.create_board(10, 10, jumped_piece=None)
droughts.create_players('White', 'Black')

droughts.create_piece('w_token', sprite='w_pawn', owner='White')
droughts.create_piece('b_token', sprite='b_pawn', owner='Black')
droughts.create_piece('w_kingtoken', sprite='w_king', owner='White')
droughts.create_piece('b_kingtoken', sprite='b_king', owner='Black')

droughts.set_initial_state([
    ['w_token', None] * 5,
    [None, 'w_token'] * 5,
    ['w_token', None] * 5,
    [None, 'w_token'] * 5,
    [None] * 10,
    [None] * 10,
    ['b_token', None] * 5,
    [None, 'b_token'] * 5,
    ['b_token', None] * 5,
    [None, 'b_token'] * 5,
])


def dfs(piece, piece_loc, board):
    def single_step_move(p, pl, brd):
        if p.endswith('_token'):
            COLOR = 1 if p[0] == 'w' else - 1
            for delta in ((COLOR, +1), (COLOR, -1)):
                if brd.in_bounds((pl[0]+delta[0], pl[1]+delta[1])):
                    if brd[pl[0]+delta[0], pl[1]+delta[1]] is None:
                        yield (pl[0]+delta[0], pl[1]+delta[1]), False
            for delta in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                if brd.in_bounds((pl[0]+(2*delta[0]), pl[1]+(2*delta[1]))):
                    if brd[pl[0]+delta[0], pl[1]+delta[1]] is not None:
                        if brd[pl[0]+delta[0], pl[1]+delta[1]][0] != p[0]:
                            if brd[pl[0]+(2*delta[0]), pl[1]+(2*delta[1])] is None:
                                yield (pl[0]+(2*delta[0]), pl[1]+(2*delta[1])), True

        elif p.endswith('_kingtoken'):
            for delta in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                for loc in brd.locs_capturable(pl, delta):
                    yield loc

    stk = [(0, piece_loc, board, None)]
    chains = defaultdict(list)
    while stk:
        d, pl, brd, fm = stk.pop()
        lm = single_step_move(piece, pl, brd)
        for move in lm:
            if move[1]:  # is a jump move
                new_brd = make_move(piece, pl, latticode.Move(move[0]), brd)
                stk.append((d+1, move[0], new_brd,
                            move[0] if fm is None else fm))
                chains[d+1].append(move[0] if fm is None else fm)
            elif d == 0:
                chains[0].append(move[0])

    if not chains:
        return set()

    max_depth = max(chains.keys())
    return set((piece_loc, m, max_depth) for m in chains[max_depth])


def legal_moves(piece, piece_loc, board):
    if piece[0] != board.current_player[0].lower():
        return []

    jumps = []  # [(piece_loc, move, depth), ...]
    if board.jumped_piece is None:
        pieces = board.player_pieces(board.current_player)
    else:
        pieces = [board.jumped_piece]

    for p, p_loc in pieces:
        jumps.extend(dfs(p, p_loc, board.copy()))

    if not jumps:
        return []

    max_depth = max(j[2] for j in jumps)
    return latticode.to_moves([j[1] for j in jumps
                               if j[2] == max_depth and j[0] == piece_loc])


def make_move(piece, piece_loc, move, board):
    new_board = board.copy()
    if piece.endswith('_token') and move.loc[0] == (9 if piece[0] == 'w' else 0):
        piece = piece[0] + '_kingtoken'
    new_board[move.loc] = piece
    is_capture = new_board.capture_diag(piece_loc, move.loc)

    if is_capture:
        new_board.jumped_piece = (piece, move.loc)
        lm = legal_moves(piece, move.loc, new_board)

        if [m for m in lm if new_board.copy().capture_diag(move.loc, m.loc)]:
            return new_board

    new_board.jumped_piece = None
    new_board.current_player = 'White' if new_board.current_player == 'Black' else 'Black'
    return new_board


def check_status(game, board):
    white_pieces = board.player_pieces('White')
    black_pieces = board.player_pieces('Black')

    if not white_pieces:
        return 'Black'
    elif not black_pieces:
        return 'White'

    if all(len(list(legal_moves(p, pl, board))) == 0 for p, pl in white_pieces):
        return 'Black'
    elif all(len(list(legal_moves(p, pl, board))) == 0 for p, pl in black_pieces):
        return 'White'

    return latticode.ONGOING


droughts.set_initial_player('Black')
droughts.set_legal_moves_function(legal_moves)
droughts.set_make_move_function(make_move)
droughts.set_check_status_function(check_status)

game = droughts
