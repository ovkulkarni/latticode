from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from asgiref.sync import async_to_sync
import json
import latticode

from .models import Game

from os.path import relpath

import importlib
import traceback
import urllib.parse


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['game_id']
        params = urllib.parse.parse_qs(self.scope['query_string'].decode())
        self.ident = params['id'][0]
        self.room_group_name = 'game_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'handle_message',
                'message': json.loads(text_data),
            }
        )

    def handle_message(self, event):
        data = event['message']
        act = data.get('action', 'wtf')
        try:
            if act == "initialize_game":
                if hasattr(self.channel_layer, 'imported_module_' + self.room_group_name):
                    # self.send(text_data=json.dumps({'ready': True}))
                    self.instance = getattr(
                        self.channel_layer, 'imported_module_' + self.room_group_name).game
                    sidelined = []
                    for piece_name in self.instance.board.sidelined_pieces:
                        if self.instance.board.sidelined_pieces[piece_name] > 0:
                            sidelined.append(piece_name)
                    self.send(text_data=json.dumps(
                        {'command': 'render', 'current': self.instance.board.current_player, 'board': self.instance.board.board, 'sprites': self.instance.piece_sprite, 'sidelined': sidelined}))
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
                setattr(self.channel_layer, 'imported_module_' +
                        self.room_group_name, importlib.import_module(
                            module_name))
                self.instance = getattr(
                    self.channel_layer, 'imported_module_' + self.room_group_name).game
                sidelined = []
                for piece_name in self.instance.board.sidelined_pieces:
                    if self.instance.board.sidelined_pieces[piece_name] > 0:
                        sidelined.append(piece_name)
                self.send(text_data=json.dumps(
                    {'command': 'render', 'current': self.instance.board.current_player, 'board': self.instance.board.board, 'sprites': self.instance.piece_sprite, 'sidelined': sidelined}))
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
                if data['ident'] == self.ident:
                    piece_name = data['name']
                    piece_loc = (data['y'], data['x']
                                 ) if data['x'] is not None else None
                    move_loc = (data['move_y'], data['move_x']
                                ) if data['move_x'] is not None else None
                    move = list(filter(lambda p: p.loc == move_loc,
                                       self.instance.legal_moves_func(piece_name, piece_loc)))[0]
                    self.instance.make_move_func(piece_name, piece_loc, move)
                    sidelined = []
                    for piece_n in self.instance.board.sidelined_pieces:
                        if self.instance.board.sidelined_pieces[piece_n] > 0:
                            sidelined.append(piece_n)
                    self.send(text_data=json.dumps(
                        {'command': 'render', 'current': self.instance.board.current_player, 'board': self.instance.board.board, 'sprites': self.instance.piece_sprite, 'sidelined': sidelined}))
                    result = self.instance.check_status_func()
                    if result != latticode.ONGOING:
                        self.send(json.dumps(
                            {'command': 'game_over', 'result': result.title()}))
                else:
                    self.send(text_data=json.dumps(
                        {'command': 'request_update'}))
            elif act == "update":
                sidelined = []
                for piece_n in self.instance.board.sidelined_pieces:
                    if self.instance.board.sidelined_pieces[piece_n] > 0:
                        sidelined.append(piece_n)
                self.send(text_data=json.dumps(
                    {'command': 'render', 'current': self.instance.board.current_player, 'board': self.instance.board.board, 'sprites': self.instance.piece_sprite, 'sidelined': sidelined}))
                result = self.instance.check_status_func()
                if result != latticode.ONGOING:
                    self.send(json.dumps(
                        {'command': 'game_over', 'result': result.title()}))
            else:
                print(data)
        except Exception:
            out = traceback.format_exc()
            self.send(json.dumps({'command': 'error', 'message': out}))
