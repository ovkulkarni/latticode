import game

chess = game.Game('Chess')
brd = chess.create_board(8, 8)
chess.create_players('white', 'black')

for player in ('white', 'black'):
    chess.create_piece('{}_pawn'.format(player[0]), owner=player)
    chess.create_piece('{}_knight'.format(player[0]), owner=player)
    chess.create_piece('{}_bishop'.format(player[0]), owner=player)
    chess.create_piece('{}_rook'.format(player[0]), owner=player)
    chess.create_piece('{}_queen'.format(player[0]), owner=player)
    chess.create_piece('{}_king'.format(player[0]), owner=player)

# brd.set_initial_state([
#     ['b_rook', 'b_knight', 'b_bishop', 'b_queen',
#         'b_king', 'b_bishop', 'b_knight', 'b_rook'],
#     ['b_pawn']*8,
#     [None]*8,
#     [None]*8,
#     [None]*8,
#     [None]*8,
#     ['w_pawn']*8,
#     ['w_rook', 'w_knight', 'w_bishop', 'w_queen',
#         'w_king', 'w_bishop', 'w_knight', 'w_rook'],
# ])

brd.set_initial_state([
    ['b_king', None, None, None, None, None, None, None],
    [None]*8,
    [None]*8,
    [None]*8,
    [None]*8,
    [None]*8,
    [None]*8,
    ['w_rook', None, None, None, None, None, None, None],
])

add = lambda *args: (sum(a[0] for a in args), sum(a[1] for a in args))


def enemy_player(p): return "black" if p[0] == 'w' else "white"


def semi_legal_moves(piece, board, player_name):
    if piece.owner != player_name:
        return []

    DELTA_DICT = {
        "queen": ((1, 1), (-1, 1), (1, -1), (-1, 1), (1, 0), (0, 1), (-1, 0), (0, -1)),
        "bishop": ((1, 1), (-1, 1), (1, -1), (-1, 1)),
        "rook": ((1, 0), (0, 1), (-1, 0), (0, -1)),
        "knight": ((2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, 1), (-2, -1))
    }

    COLOR = 1 if player_name == 'black' else -1

    pt = piece.name[piece.name.index("_") + 1:]

    moves = []
    if pt == "king":
        moves.extend(
            board.moves_in_radius(piece.loc, 2))
        # O-O
        # O-O-O
    if pt == "queen" or pt == "rook" or pt == "bishop":
        for delta in DELTA_DICT[pt]:
            moves.extend(
                board.moves_visible_in_dir(piece.loc, delta))
    if pt == "knight":
        for delta in DELTA_DICT[pt]:
            move = board.move_in_dir(piece.loc, delta)
            if move is not None:
                moves.append(move)
    if pt == "pawn":
        # forward moves
        if board[add(piece.loc, (1*COLOR, 0))] is None:
            moves.append(add(piece.loc, (1*COLOR, 0)))
            if piece.moves_made == 0 and board[add(piece.loc, (2*COLOR, 0))] is None:
                moves.append(add(piece.loc, (2 * COLOR, 0)))
        # captures
        for delta in ((1 * COLOR, 1), (1 * COLOR, -1)):
            move = add(piece.loc, delta)
            if 0 <= move[0] < board.dims[0] and 0 <= move[1] < board.dims[1]:
                if board[move] is not None and board[move].owner != player:
                    moves.append(add(piece.loc, delta))

        # en passant
        if piece.loc[0] in (3, 4):
            for side in ((0, 1), (0, -1)):
                captee = board[add(piece.loc, side)]
                if captee is None:
                    continue
                if captee.owner != player and captee.moves_made == 1 and board.past[-1].piece == captee:
                    moves.append(add(piece.loc, (1 * COLOR, side[1])))

    moves = filter(
        lambda m: (board[m] is None or board[m].owner != player_name), moves)

    return list(moves)


def checked(board, player):
    my_king = None
    for piece in board.player_pieces(player):
        if piece.name.endswith("king"):
            my_king = piece
            break
    for piece in board.player_pieces(enemy_player(player)):
        if my_king.loc in semi_legal_moves(piece, board, enemy_player(player)):
            return True
    return False


def legal_moves(piece, board, player):
    moves = semi_legal_moves(piece, board, player)
    checkless_moves = []
    for move in moves:
        temp = board.clone()
        make_move(move, piece, temp, player)
        if not checked(temp, player):
            checkless_moves.append(move)
    return checkless_moves


def make_move(move, piece, board, player):
    board[piece.loc] = None
    board[move] = piece
    return enemy_player(player)


def check_win(board, player):
    return board.in_row(length=3, piece=player)


chess.set_initial_player('black')
chess.set_legal_moves_function(legal_moves)
chess.set_make_move_function(make_move)
chess.set_check_win_function(check_win)

king = chess.board[(0, 0)]
print(king)
print(chess.legal_moves_func(king))
print(brd)
