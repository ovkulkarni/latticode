import game

ttt = game.Game('Chess')
brd = ttt.create_board(8, 8)
ttt.create_players('white', 'black')

for prefix in ('white', 'black'):
    ttt.create_piece('{}_pawn'.format(prefix[0]), owner=prefix)
    ttt.create_piece('{}_knight'.format(prefix[0]), owner=prefix)
    ttt.create_piece('{}_bishop'.format(prefix[0]), owner=prefix)
    ttt.create_piece('{}_rook'.format(prefix[0]), owner=prefix)
    ttt.create_piece('{}_queen'.format(prefix[0]), owner=prefix)
    ttt.create_piece('{}_king'.format(prefix[0]), owner=prefix)

brd.initial_state([
    ['b_rook', 'b_knight', 'b_bishop', 'b_queen',
        'b_king', 'b_bishop', 'b_knight', 'b_rook'],
    ['b_pawn']*8,
    [0]*8,
    [0]*8,
    [0]*8,
    [0]*8,
    ['w_pawn']*8,
    ['w_rook', 'w_knight', 'w_bishop', 'w_queen',
        'w_king', 'w_bishop', 'w_knight', 'w_rook'],
])

add = lambda *args: (sum(a[0] for a in args), sum(a[1] for a in args))


def enemy_player(p): return "black" if p[0] == 'w' else "white"


def semi_legal_moves(piece, board, player):
    if piece.owner != player.name:
        return []

    DELTA_DICT = {
        "queen": ((1, 1), (-1, 1), (1, -1), (-1, 1), (1, 0), (0, 1), (-1, 0), (0, -1)),
        "bishop": ((1, 1), (-1, 1), (1, -1), (-1, 1)),
        "rook": ((1, 0), (0, 1), (-1, 0), (0, -1)),
        "knight": ((2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, 1), (-2, -1))
    }

    COLOR = -1 if player.name == 'black' else 1

    pt = piece.name[piece.name.index("_") + 1:]

    moves = []
    if pt == "king":
        moves.extend(
            board.cells_in_radius(piece.loc, 2))
        # O-O
        # O-O-O
    if pt == "queen" or pt == "rook" or pt == "bishop":
        for delta in DELTA_DICT[pt]:
            moves.extend(
                board.cells_visible_in_dir(piece.loc, delta))
    if pt == "knight":
        for delta in DELTA_DICT[pt]:
            moves.extend(board.cell_in_dir(piece.loc, delta))
    if pt == "pawn":
        # forward moves
        if board.is_open(add(piece.loc, (1*COLOR, 0))):
            moves.append(add(piece.loc, (1*COLOR, 0)))
            if piece.moves_made == 0 and board.is_open(add(piece.loc, (2*COLOR, 0))):
                moves.append(add(piece.loc, (2 * COLOR, 0)))
        # captures
        for delta in ((1 * COLOR, 1), (1 * COLOR, -1)):
            if board[add(piece.loc, delta)].owner != player.name:
                moves.append(add(piece.loc, delta))
        # en passant
        if piece.loc[0] in (3, 4):
            for side in ((0, 1), (0, -1)):
                captee = board[add(piece.loc, side)]
                if captee.owner != player.name and captee.moves_made == 1 and board.past[-1].id == captee.id:
                    moves.append(add(piece.loc, (1 * COLOR, side[1])))

    if pt != "pawn":
        moves = filter(
            moves, lambda m: not board[m] or board[m].owner != player.name)

    return moves


def checked(board, player):
    my_king = None
    for piece in board.ally_pieces(player):
        if piece.endswith("king"):
            my_king = piece
            break
    for piece in board.enemy_pieces(player):
        if my_king.loc in semi_legal_moves(piece, board, enemy_player(player)):
            return True
    return False


def legal_moves(piece, board, player):
    moves = semi_legal_moves(piece, board, player)
    checkless_moves = []
    for move in moves:
        temp = board.temporary_copy()
        make_move(move, piece, temp, player)
        if not checked(temp, player):
            checkless_moves.append(move)
    return checkless_moves


def make_move(move, piece, board, player):
    board[piece.loc] = None
    board[move] = piece


def check_win(board, player):
    return board.in_row(length=3, piece=player.name)


ttt.set_legal_moves_function(legal_moves)
ttt.set_make_moves_function(make_move)
ttt.set_check_win_function(check_win)
