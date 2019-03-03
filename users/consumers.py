from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
import json
import latticode

from .models import Game

from os.path import relpath

import importlib
import traceback


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        act = data.get('action', 'wtf')
        try:
            if act == "initialize_game":
                if hasattr(self, 'imported_module'):
                    self.send(text_data=json.dumps({'ready': True}))
                    return
                try:
                    obj_id = data.get('id', -1)
                    g = Game.objects.get(id=obj_id)
                except Game.DoesNotExist:
                    self.send(text_data=json.dumps(
                        {'error': 'Game not found'}))
                    return
                diff = relpath(str(g.code), settings.BASE_DIR)
                module_name = diff.replace(".py", "").replace("/", ".")
                self.imported_module = importlib.import_module(module_name)
                self.instance = self.imported_module.game
                sidelined = []
                for piece_name in self.instance.board.sidelined_pieces:
                    if self.instance.board.sidelined_pieces[piece_name] > 0:
                        sidelined.append(piece_name)
                self.send(text_data=json.dumps(
                    {'command': 'render', 'board': self.instance.board.board, 'sprites': self.instance.piece_sprite, 'sidelined': sidelined}))
            elif act == "get_legal":
                piece = data['name']
                sidelined = []
                for piece_name in self.instance.board.sidelined_pieces:
                    if self.instance.board.sidelined_pieces[piece_name] > 0:
                        sidelined.append(piece_name)
                if data['x'] is not None and data['y'] is not None:
                    self.send(text_data=json.dumps({
                        'command': 'legal', 'board': self.instance.board.board, 'sidelined': sidelined,
                        'positions': [x.loc for x in self.instance.legal_moves_func(piece, (int(data['y']), int(data['x'])))]}))
                else:
                    self.send(text_data=json.dumps({
                        'command': 'legal', 'board': self.instance.board.board, 'sidelined': sidelined,
                        'positions': [x.loc for x in self.instance.legal_moves_func(piece, None)]}))
            elif act == "make_move":
                piece_name = data['name']
                piece_loc = (data['y'], data['x']
                             ) if data['x'] is not None else None
                move_loc = (data['move_y'], data['move_x']
                            ) if data['move_x'] is not None else None
                move = list(filter(lambda p: p.loc == move_loc,
                                   self.instance.legal_moves_func(piece_name, piece_loc)))[0]
                self.instance.make_move_func(piece_name, piece_loc, move)
                sidelined = []
                for piece_name in self.instance.board.sidelined_pieces:
                    if self.instance.board.sidelined_pieces[piece_name] > 0:
                        sidelined.append(piece_name)
                self.send(text_data=json.dumps(
                    {'command': 'render', 'board': self.instance.board.board, 'sprites': self.instance.piece_sprite, 'sidelined': sidelined}))
                result = self.instance.check_status_func()
                if result != latticode.ONGOING:
                    self.send(json.dumps(
                        {'command': 'game_over', 'result': result.title()}))
            else:
                print(data)
        except Exception:
            out = traceback.format_exc()
            self.send(json.dumps({'command': 'error', 'message': out}))
