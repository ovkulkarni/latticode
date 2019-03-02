import math
from collections import defaultdict

# TODO: ADD ASSERTIONS
# TODO: ADD BS DOCUMENTATION

### CONSTANTS ###
EMPTY_BOARD = 0
INFINITY = math.inf

### CLASSES ###


def in_bounds(pos, dims):
    return (0 <= pos[0] < dims[0] and
            0 <= pos[1] < dims[1])


class Board():
    def __init__(self, game, x, y, *args):
        self.game = game
        self.board = None
        self.dims = (x, y)
        self.sidelined_pieces = defaultdict(lambda: 0)

    def __str__(self):
        if self.board is None:
            return "Board not yet set."
        return "\n".join(' '.join('.' if x is None else str(x) for x in r)
                         for r in self.board)

    def __setitem__(self, key, value):
        self.board[key[1]][key[0]] = value

    def set_initial_state(self, state):
        if state == EMPTY_BOARD:
            self.board = [[None for _ in range(
                self.dims[0])] for _ in range(self.dims[1])]
        else:
            self.board = state

    def add_sidelined_piece(self, p_id, count):
        self.sidelined_pieces[p_id] += count

    def open_spaces(self):
        to_ret = []
        for x in range(self.dims[0]):
            for y in range(self.dims[1]):
                if self.board[y][x] is None:
                    to_ret.append((x, y))
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


class Player():
    def __init__(self, player_name):
        self.name = player_name

    def __str__(self):
        return "Player -> name:{}".format(self.name)


def Piece(piece_name, piece_sprite):
    class p():
        def __init__(self):
            self.name = piece_name
            self.sprite = piece_sprite

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

    def create_piece(self, piece_id, sprite):
        self.pieces[piece_id] = Piece(piece_id, sprite)

    def get_board(self):
        return self.board

    def get_player(self, p_id):
        return self.players[p_id]

    def get_piece(self, p_id):
        return self.pieces[p_id]

    def set_initial_player(self, p_id):
        self.mover = self.get_player(p_id)

    def set_legal_moves_function(self, legal_moves):
        self.legal_moves_func = legal_moves

    def set_make_moves_function(self, make_move):
        self.make_moves_func = make_move

    def set_check_win_function(self, check_win):
        self.check_win_func = check_win
