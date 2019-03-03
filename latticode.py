from math import inf
from copy import deepcopy
from collections import defaultdict, namedtuple

### CONSTANTS ###
EMPTY_BOARD = 0
TIE = 'tie'
ONGOING = 'ongoing'
INFINITY = inf

Delta = namedtuple('Delta', 'piece_name piece_loc move')


class Move():
    def __init__(self, loc, movetype=None, **kwargs):
        self.loc = loc
        self.movetype = movetype
        self.__dict__.update(kwargs)

    def __repr__(self):
        return str(self.loc) + ("" if self.movetype is None else "_{}".format(self.movetype))


class Board():
    def __init__(self, x, y, game, **kwargs):
        assert isinstance(x, int) and isinstance(
            y, int), "X and Y must be integers."
        self.board = None
        self.dims = (x, y)
        self.sidelined_pieces = defaultdict(lambda: 0)
        self.current_player = None
        self.game = game

        self.cloneable_attributes = kwargs.keys()
        self.__dict__.update(kwargs)

    def __str__(self):
        assert self.board is not None, "Board has not been created yet."
        format_width = max(map(len, self.game.pieces))
        fmt = '\t'.join('{{:^{}}}'.format(format_width)
                        for _ in range(self.dims[0]))
        table = [fmt.format(
            *row) for row in [['.' if c is None else c for c in r] for r in self.board]]
        return '\n'.join(table)

    def __setitem__(self, key, value):
        assert self.board is not None, "Board has not been created yet."
        self.board[key[0]][key[1]] = value

    def __getitem__(self, key):
        assert self.board is not None, "Board has not been created yet."
        return self.board[key[0]][key[1]]

    def copy(self):
        brd = Board(*self.dims, self.game)
        brd.board = [[c for c in r] for r in self.board]
        brd.sidelined_pieces = self.sidelined_pieces.copy()
        brd.current_player = self.current_player

        brd.__dict__.update({k: deepcopy(self.__dict__[k])
                             for k in self.cloneable_attributes})
        return brd

    def in_bounds(self, loc):
        return 0 <= loc[0] < self.dims[0] and 0 <= loc[1] < self.dims[1]

    def open_spaces(self):
        to_ret = []
        for x in range(self.dims[0]):
            for y in range(self.dims[1]):
                if self.board[y][x] is None:
                    to_ret.append((y, x))
        return to_ret

    def open_spaces_gravity(self):
        to_ret = []
        for x in range(self.dims[0]):
            for y in reversed(range(self.dims[1])):
                if self.board[y][x] is None:
                    to_ret.append((y, x))
                    break
        return to_ret

    def in_row(self, length, piece):
        for y in range(self.dims[1]):
            count = 0
            for x in range(self.dims[0]):
                val = self.board[y][x]
                if val is not None and val == piece:
                    count += 1
                else:
                    count = 0
                if count >= length:
                    return True
        return False

    def in_col(self, length, piece):
        for x in range(self.dims[0]):
            count = 0
            for y in range(self.dims[1]):
                val = self.board[y][x]
                if val is not None and val == piece:
                    count += 1
                else:
                    count = 0
                if count >= length:
                    return True
        return False

    def in_diag(self, length, piece):
        def check_delta(pos, d):
            count = 0
            pointer = pos
            while self.in_bounds(pointer):
                if (self.board[pointer[1]][pointer[0]] is not None and
                        self.board[pointer[1]][pointer[0]] == piece):
                    count += 1
                else:
                    count = 0
                if count >= length:
                    return True
                pointer = (pointer[0] + d[0], pointer[1] + d[1])
            return False

        positions_to_check = [(0, y) for y in range(self.dims[1])]
        positions_to_check += [(x, 0) for x in range(self.dims[0])]
        positions_to_check += [(self.dims[0]-1, y)
                               for y in range(self.dims[1])]

        for pos in positions_to_check:
            if check_delta(pos, (1, 1)) or check_delta(pos, (1, -1)):
                return True
        return False

    def in_line(self, length, piece):
        if self.in_row(length=3, piece=piece):
            return True
        if self.in_col(length=3, piece=piece):
            return True
        elif self.in_diag(length=3, piece=piece):
            return True
        return False

    def move_in_dir(self, loc, delta):
        if self.in_bounds((loc[0] + delta[0], loc[1] + delta[1])):
            return (loc[0] + delta[0], loc[1] + delta[1])
        return None

    def moves_visible_in_dir(self, loc, delta):
        pointer = (loc[0] + delta[0], loc[1] + delta[1])
        while self.in_bounds(pointer) and self[pointer] is None:
            yield pointer
            pointer = (pointer[0] + delta[0], pointer[1] + delta[1])
        if self.in_bounds(pointer):
            yield pointer

    def moves_in_radius(self, loc, r2):
        for y in range(loc[0]-r2, loc[0]+r2+1):
            for x in range(loc[1]-r2, loc[1]+r2+1):
                if (loc[0]-y)**2 + (loc[1]-x)**2 <= r2 and self.in_bounds((y, x)):
                    yield (y, x)

    def player_pieces(self, player_name):
        for x in range(self.dims[0]):
            for y in range(self.dims[1]):
                if self[(x, y)] is not None and self.game.piece_owner[self[(x, y)]] == player_name:
                    yield self[(x, y)]

    def all_filled(self):
        for x in range(self.dims[0]):
            for y in range(self.dims[1]):
                if self.board[y][x] is None:
                    return False
        return True


class Game():
    def __init__(self, name):
        self.game_name = name
        self.board = None
        self.players = []
        self.past = []
        self.pieces = set()
        self.piece_sprite = {}
        self.piece_owner = {}

    def create_board(self, x, y, **kwargs):
        self.board = Board(x, y, self, **kwargs)
        return self.board

    def create_players(self, *players):
        self.players.extend(players)
        return self.players

    def create_piece(self, piece_name, sprite=None, owner=None):
        self.pieces.add(piece_name)
        self.piece_sprite[piece_name] = sprite if sprite is not None else piece_name
        self.piece_owner[piece_name] = owner

    def get_board(self):
        assert self.board is not None, "Board has not been created yet."
        return self.board

    def set_initial_player(self, player):
        assert player in self.players, "{} is not a valid player.".format(
            player)
        self.board.current_player = player

    def set_initial_state(self, state):
        assert self.board is not None, "Board has not been created yet."
        if state == EMPTY_BOARD:
            self.board.board = [[None for _ in range(
                self.board.dims[0])] for _ in range(self.board.dims[1])]
        else:
            assert isinstance(state, list), "Board must be a 2D list."
            assert isinstance(state[0], list), "Board must be a 2D list."
            assert len(state) == self.board.dims[1] and len(
                state[0]) == self.board.dims[0], "board must be {}x{}".format(*self.board.dims)
            assert all(p in self.pieces or p is None for p in sum(
                state, [])), "Invalid pieces in initial state."
            self.board.board = state

    def add_sidelined_piece(self, piece, count):
        assert piece in self.pieces, "{} is not a valid piece.".format(piece)
        self.board.sidelined_pieces[piece] += count

    def set_legal_moves_function(self, legal_moves):
        def lmf(piece, piece_loc):
            return legal_moves(piece, piece_loc, self.board)
        self.legal_moves_func = lmf

    def set_make_move_function(self, make_move):
        def mm(piece, piece_loc, move):
            self.board = make_move(piece, piece_loc, move, self.board)
            if piece_loc is None:  # piece just placed
                self.board.sidelined_pieces[piece] -= 1
            self.past.append(Delta(piece, piece_loc, move))
        self.make_move_func = mm

    def set_check_status_function(self, check_status):
        def wf():
            return check_status(self, self.board)
        self.check_status_func = wf
