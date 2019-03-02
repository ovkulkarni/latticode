import math
from collections import defaultdict

# TODO: ADD ASSERTIONS

### CONSTANTS ###
EMPTY_BOARD = 0
INFINITY = math.inf

### CLASSES ###


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
