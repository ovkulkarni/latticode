import math
import uuid
from collections import defaultdict, namedtuple

# TODO: ADD ASSERTIONS
# TODO: ADD BS DOCUMENTATION

### CONSTANTS ###
EMPTY_BOARD = 0
INFINITY = math.inf


def in_bounds(pos, dims):
    return (0 <= pos[0] < dims[0] and
            0 <= pos[1] < dims[1])


PastElement = namedtuple('PastTuple', 'piece move')


class Board():
    def __init__(self, game, x, y, *args):
        assert isinstance(x, int) and isinstance(
            y, int), "x and y must be integers"
        self.game = game
        self.board = None
        self.dims = (x, y)
        self.sidelined_pieces = defaultdict(lambda: 0)
        self.past = []

    def __str__(self):
        assert self.board is not None, "board has not been created yet"
        return "\n".join(' '.join('.' if x is None else str(x) for x in r)
                         for r in self.board)

    def __setitem__(self, key, value):
        assert self.board is not None, "board has not been created yet"
        self.board[key[0]][key[1]] = value

    def __getitem__(self, key):
        assert self.board is not None, "board has not been created yet"
        return self.board[key[0]][key[1]]

    def set_initial_state(self, state):
        if state == EMPTY_BOARD:
            self.board = [[None for _ in range(
                self.dims[0])] for _ in range(self.dims[1])]
        else:
            assert isinstance(state, list), "Board must be a 2D list"
            assert isinstance(state[0], list), "Board must be a 2D list"
            assert len(state) == self.dims[1] and len(
                state[0]) == self.dims[0], "board must be {}x{}".format(*self.dims)
            for y in range(self.dims[1]):
                for x in range(self.dims[0]):
                    if state[y][x] is not None:
                        assert state[y][x] in self.game.pieces, "{} is not a valid piece.".format(
                            state[y][x])
                        state[y][x] = self.game.pieces[state[y][x]](loc=(y, x))
            self.board = state

    def add_sidelined_piece(self, p_id, count):
        assert p_id in self.game.pieces, "{} is not a valid piece.".format(
            p_id)
        self.sidelined_pieces[p_id] += count

    def open_spaces(self):
        to_ret = []
        for x in range(self.dims[0]):
            for y in range(self.dims[1]):
                if self.board[y][x] is None:
                    to_ret.append((y, x))
        return to_ret

    def in_row(self, length, piece):
        for y in range(self.dims[1]):
            count = 0
            for x in range(self.dims[0]):
                val = self.board[y][x]
                if val is not None and val.name == piece:
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
                if val is not None and val.name == piece:
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
            while in_bounds(pointer, self.dims):
                if (self.board[pointer[1]][pointer[0]] is not None and
                        self.board[pointer[1]][pointer[0]].name == piece):
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

    def move_in_dir(self, loc, delta):
        if in_bounds((loc[0] + delta[0], loc[1] + delta[1]), self.dims):
            return (loc[0] + delta[0], loc[1] + delta[1])
        return None

    def moves_visible_in_dir(self, loc, delta):
        pointer = (loc[0] + delta[0], loc[1] + delta[1])
        while in_bounds(pointer, self.dims) and self[pointer] is None:
            yield pointer
            pointer = (pointer[0] + delta[0], pointer[1] + delta[1])
        if in_bounds(pointer, self.dims):
            yield pointer

    def moves_in_radius(self, loc, r2):
        for y in range(loc[0]-r2, loc[0]+r2+1):
            for x in range(loc[1]-r2, loc[1]+r2+1):
                if (loc[0]-y)**2 + (loc[1]-x)**2 <= r2 and in_bounds((y, x), self.dims):
                    yield (y, x)


class Player():
    def __init__(self, player_name):
        self.name = player_name

    def __str__(self):
        return "Player -> name:{}".format(self.name)


def Piece(name, sprite, **kwargs):
    class p():
        def __init__(self, loc=None):
            self.name = name
            self.sprite = sprite if sprite is not None else name
            self.uuid = uuid.uuid4()
            self.loc = loc
            self.moves_made = 0
            self.__dict__.update(kwargs)

        def __eq__(self, other):
            return self.uuid == other.uuid

        def __str__(self):
            return self.sprite

    return p


class Game():
    def __init__(self, name):
        self.game_name = name
        self.board = None
        self.mover = None
        self.players = {}
        self.pieces = {}

    def create_board(self, *args):
        self.board = Board(self, *args)
        return self.board

    def create_players(self, *player_ids):
        for p_id in player_ids:
            self.players[p_id] = Player(p_id)
        return self.players

    def create_piece(self, piece_id, sprite=None, **kwargs):
        self.pieces[piece_id] = Piece(
            piece_id, sprite if sprite is not None else piece_id, **kwargs)

    def get_board(self):
        return self.board

    def get_player(self, p_id):
        assert p_id in self.players, "{} is not a valid player".format(p_id)
        return self.players[p_id]

    def get_piece(self, p_id):
        assert p_id in self.pieces, "{} is not a valid player".format(p_id)
        assert self.board.sidelined_pieces[p_id] > 0, "You don't have any available {}s".format(
            p_id)

        self.board.sidelined_pieces[p_id] -= 1
        return self.pieces[p_id](loc=None)

    def set_initial_player(self, p_id):
        assert p_id in self.players, "{} is not a valid player".format(p_id)
        self.mover = self.get_player(p_id)

    def set_legal_moves_function(self, legal_moves):
        def lmf(piece):
            return legal_moves(piece, self.board, self.mover)
        self.legal_moves_func = lmf

    def set_make_move_function(self, make_move):
        def mm(move, piece):
            piece.moves_made += 1
            piece.loc = move
            self.board.past.append(PastElement(piece, move))
            player_string = make_move(move, piece, self.board, self.mover)
            self.mover = self.get_player(player_string)
        self.make_move_func = mm

    def set_check_win_function(self, check_win):
        def wf(player):
            return check_win(self.board, player)
        self.check_win_func = wf
