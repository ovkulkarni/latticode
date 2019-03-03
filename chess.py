import latticode
from latticode import Move, to_moves, to_locs

game = latticode.Game('Chess')
brd = game.create_board(8, 8,
                        enpassantable=None,
                        castle={"white": [True, True],
                                "black": [True, True]}
                        )
game.create_players('white', 'black')

for player in game.players:
    game.create_piece('{}_pawn'.format(player[0]), owner=player)
    game.create_piece('{}_knight'.format(player[0]), owner=player)
    game.create_piece('{}_bishop'.format(player[0]), owner=player)
    game.create_piece('{}_rook'.format(player[0]), owner=player)
    game.create_piece('{}_queen'.format(player[0]), owner=player)
    game.create_piece('{}_king'.format(player[0]), owner=player)

game.set_initial_state([
    ['b_rook', 'b_knight', 'b_bishop', 'b_queen',
        'b_king', 'b_bishop', 'b_knight', 'b_rook'],
    ['b_pawn']*8,
    [None]*8,
    [None]*8,
    [None]*8,
    [None]*8,
    ['w_pawn']*8,
    ['w_rook', 'w_knight', 'w_bishop', 'w_queen',
        'w_king', 'w_bishop', 'w_knight', 'w_rook'],
])


def add(*args): return (sum(a[0] for a in args), sum(a[1] for a in args))


def enemy_player(p): return "black" if p[0] == 'w' else "white"


def clip(s): return None if s is None else s[s.index("_") + 1:]


DELTA_DICT = {
    "queen": ((1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (0, 1), (-1, 0), (0, -1)),
    "bishop": ((1, 1), (-1, 1), (1, -1), (-1, -1)),
    "rook": ((1, 0), (0, 1), (-1, 0), (0, -1)),
    "knight": ((2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, 1), (-2, -1))
}


def semi_legal_moves(piece, piece_loc, board, player=None):
    player = player if player is not None else board.current_player
    pt = clip(piece)
    COLOR = 1 if player == 'black' else - 1
    BACK = 0 if player == 'black' else 7
    locs, moves = [], []

    if game.piece_owner[piece] != player:
        return []

    if pt == "king":
        locs.extend(board.locs_in_radius(piece_loc, 2))
        if board.castle[player][0] and [clip(board[BACK, a]) for a in range(4, 8)] == ["king", None, None, "rook"]:
            moves.append(Move((BACK, 6), move_type="O-O"))
        if board.castle[player][1] and [clip(board[BACK, a]) for a in range(5)] == ["rook", None, None, None, "king"]:
            moves.append(Move((BACK, 2), move_type="O-O-O"))
    if pt == "queen" or pt == "rook" or pt == "bishop":
        for delta in DELTA_DICT[pt]:
            locs.extend(board.locs_visible_in_dir(piece_loc, delta))
    if pt == "knight":
        locs.extend(board.locs_at_dirs(piece_loc, DELTA_DICT[pt]))
    if pt == "pawn":
        if board[add(piece_loc, (1*COLOR, 0))] is None:
            locs.append(add(piece_loc, (1*COLOR, 0)))
            if piece_loc[0] in (1, 6) and board[add(piece_loc, (2 * COLOR, 0))] is None:
                moves.append(
                    Move(add(piece_loc, (2 * COLOR, 0)), move_type="pawn_rush"))
        for delta in ((1 * COLOR, 1), (1 * COLOR, -1)):
            move = add(piece_loc, delta)
            if board.in_bounds(move) and board[move] is not None and game.piece_owner[board[move]] != player:
                locs.append(add(piece_loc, delta))
        for side in ((0, 1), (0, -1)):
            captee_loc = add(piece_loc, side)
            if captee_loc == board.enpassantable and game.piece_owner[board[captee_loc]] != player:
                moves.append(Move(
                    add(piece_loc, (1*COLOR, side[1])),
                    move_type="enpassant",
                    capture_loc=captee_loc
                ))

    return moves + [Move(l) for l in locs if game.piece_owner.get(board[l]) != player]


def in_check(board, player):
    king_loc = next(board.piece_locs("{}_king".format(player[0])))
    for piece, piece_loc in board.player_pieces(enemy_player(player)):
        if king_loc in to_locs(semi_legal_moves(piece, piece_loc, board, enemy_player(player))):
            return True
    return False


def legal_moves(piece, piece_loc, board):
    checkless_moves = []
    for move in semi_legal_moves(piece, piece_loc, board):
        temp = make_move(piece, piece_loc, move, board)
        if move.move_type in ("O-O", "O-O-O") and in_check(board, board.current_player):
            continue
        if not in_check(temp, board.current_player):
            checkless_moves.append(move)
    return checkless_moves


def make_move(piece, piece_loc, move, board):
    BACK = 0 if board.current_player == 'black' else 7
    new_board = board.copy()
    new_board.enpassantable = None

    if move.move_type == "enpassant":
        new_board[move.capture_loc] = None
    if move.move_type == "pawn_rush":
        new_board.enpassantable = move.loc
    if move.move_type == "O-O":
        new_board[BACK, 5], new_board[BACK, 7] = new_board[BACK, 7], None
    if move.move_type == "O-O-O":
        new_board[BACK, 3], new_board[BACK, 0] = new_board[BACK, 0], None
    if piece.endswith("pawn") and move.loc[0] in (0, 7):
        piece = "{}_queen".format(piece[0])
    if (piece.endswith("rook") and piece_loc[1] == 7) or piece.endswith("king"):
        new_board.castle[board.current_player][0] = False
    if (piece.endswith("rook") and piece_loc[1] == 0) or piece.endswith("king"):
        new_board.castle[board.current_player][1] = False

    new_board[piece_loc] = None
    new_board[move.loc] = piece
    new_board.current_player = enemy_player(board.current_player)
    return new_board


def check_status(game, board):
    if not sum(len(legal_moves(*t, board)) for t in board.player_pieces(board.current_player)):
        if in_check(board, board.current_player):
            return enemy_player(board.current_player)
        return latticode.TIE
    return latticode.ONGOING


game.set_initial_player('white')
game.set_legal_moves_function(legal_moves)
game.set_make_move_function(make_move)
game.set_check_status_function(check_status)
