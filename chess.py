import latticode
from latticode import Move
from collections import namedtuple

game = latticode.Game('Chess')
brd = game.create_board(8, 8,
                        enpassantable=None,
                        castle={"white": [True, True],
                                "black": [True, True]}
                        )
game.create_players('white', 'black')

for player in ('white', 'black'):
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

# game.set_initial_state([
#     ['w_king']+[None]*7,
#     [None]*8,
#     [None]*8,
#     [None]*8,
#     [None]*8,
#     [None]*8,
#     [None]*8,
#     ['b_rook']+[None]*7,
# ])

add = lambda *args: (sum(a[0] for a in args), sum(a[1] for a in args))


def enemy_player(p): return "black" if p[0] == 'w' else "white"


DELTA_DICT = {
    "queen": ((1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (0, 1), (-1, 0), (0, -1)),
    "bishop": ((1, 1), (-1, 1), (1, -1), (-1, -1)),
    "rook": ((1, 0), (0, 1), (-1, 0), (0, -1)),
    "knight": ((2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, 1), (-2, -1))
}


def semi_legal_moves(piece, piece_loc, board):
    player = board.current_player

    if game.piece_owner[piece] != player:
        return []

    pt = piece[piece.index("_") + 1:]

    COLOR = 1 if player == 'black' else - 1
    BACK = 0 if player == 'black' else 7

    locs = []
    moves = []
    if pt == "king":
        locs.extend(
            board.moves_in_radius(piece_loc, 2))
        # O-O
        if board.castle[player][0] and all(board[BACK, a] is None for a in (5, 6)):
            moves.append(Move((BACK, 6), move_type="O-O"))
        # O-O-O
        if board.castle[player][1] and all(board[BACK, a] is None for a in (1, 2, 3)):
            moves.append(Move((BACK, 2), move_type="O-O-O"))
    if pt == "queen" or pt == "rook" or pt == "bishop":
        for delta in DELTA_DICT[pt]:
            locs.extend(
                board.moves_visible_in_dir(piece_loc, delta))
    if pt == "knight":
        for delta in DELTA_DICT[pt]:
            move = board.move_in_dir(piece_loc, delta)
            if move is not None:
                locs.append(move)
    if pt == "pawn":
        # forward moves
        if board[add(piece_loc, (1*COLOR, 0))] is None:
            locs.append(add(piece_loc, (1*COLOR, 0)))
            if piece_loc[0] in (1, 6) and board[add(piece_loc, (2 * COLOR, 0))] is None:
                moves.append(Move(add(piece_loc, (2 * COLOR, 0)), move_type="pawn_rush",
                                  ))
        # captures
        for delta in ((1 * COLOR, 1), (1 * COLOR, -1)):
            move = add(piece_loc, delta)
            if board.in_bounds(move) and board[move] is not None and game.piece_owner[board[move]] != player:
                locs.append(add(piece_loc, delta))

        # en passant
        if piece_loc[0] in (3, 4):
            for side in ((0, 1), (0, -1)):
                captee_loc = add(piece_loc, side)
                if board[captee_loc] is None:
                    continue
                if game.piece_owner[board[captee_loc]] != player and captee_loc == board.enpassantable:
                    moves.append(Move(
                        add(piece_loc, (1*COLOR, side[1])),
                        move_type="enpassant",
                        capture_loc=captee_loc
                    ))

    locs = filter(
        lambda m: (board[m] is None or game.piece_owner[board[m]] != player), locs)

    moves.extend([Move(loc) for loc in locs])
    return moves


def king_loc_of(board, player):
    for piece, piece_loc in board.player_pieces(player):
        if piece.endswith("king"):
            return piece_loc


def in_check(board, player):
    king_loc = king_loc_of(board, player)
    for piece, piece_loc in board.player_pieces(enemy_player(player)):
        moves = semi_legal_moves(piece, piece_loc, board)
        if king_loc in [m.loc for m in moves]:
            return True
    return False


def legal_moves(piece, piece_loc, board):
    moves = semi_legal_moves(piece, piece_loc, board)
    checkless_moves = []
    for move in moves:
        temp = make_move(piece, piece_loc, move, board)
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
        new_board[BACK, 5] = new_board[BACK, 7]
        new_board[BACK, 7] = None
    if move.move_type == "O-O-O":
        new_board[BACK, 3] = new_board[BACK, 0]
        new_board[BACK, 0] = None
    if piece.endswith("pawn") and move.loc[0] in (0, 7):
        piece = "{}_queen".format(piece[0])
    new_board[piece_loc] = None
    new_board[move.loc] = piece
    new_board.current_player = enemy_player(board.current_player)
    return new_board


def check_status(game, board):
    for player in game.players:
        king = king_loc_of(board, player)
        if in_check(board, player) and len(legal_moves("{}_king".format(player[0]), king, board)) == 0:
            return enemy_player(player)
    return latticode.ONGOING


game.set_initial_player('white')
game.set_legal_moves_function(legal_moves)
game.set_make_move_function(make_move)
game.set_check_status_function(check_status)

# print(game.legal_moves_func("w_king", (0, 0)))

# game.make_move_func("w_pawn", (6, 4), Move((4, 4), "pawn_rush"))
# game.make_move_func("b_knight", (0, 1), Move((2, 0)))
# game.make_move_func("w_pawn", (4, 4), Move((3, 4)))
# game.make_move_func("b_pawn", (1, 3), Move((3, 3), "pawn_rush"))

# mvs = game.legal_moves_func("w_pawn", (3, 4))
# game.make_move_func("w_pawn", (3, 4), mvs[0])

# game.make_move_func("b_bishop", (0, 2), Move((2, 4)))
# game.make_move_func("w_pawn", (2, 3), Move((1, 4)))
# game.make_move_func("b_queen", (0, 3), Move((2, 3)))
# game.make_move_func("w_pawn", (1, 4), Move((0, 5)))
# game.make_move_func("b_queen", (2, 3), Move((0, 5)))
# game.make_move_func("w_queen", (7, 3), Move((6, 4)))
# game.make_move_func("b_king", (0, 4), Move((0, 2), "O-O-O"))
# print(game.board, "\n")
