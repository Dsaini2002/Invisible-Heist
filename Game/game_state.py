from player import MrX, Detective

import sys
sys.path.append('.')
sys.path.append('..')
from Map.routes import get_locations
import random

class GameState:
    def __init__(self, max_detectives=4):
        self.positions = get_locations()
        self.players = {}  # role -> Player instance
        self.turn_order = []  # list of role strings
        self.current_turn_index = 0
        self.max_detectives = max_detectives

    def add_player(self, role=None):
        if "MrX" not in self.players:
            role = "MrX"
            player = MrX(self._get_random_position())
        else:
            num = len([r for r in self.players if r.startswith("D")]) + 1
            role = f"D{num}"
            player = Detective(role, self._get_random_position())
        
        self.players[role] = player
        self.turn_order.append(role)
        return role

    def _get_random_position(self):
        return random.choice(list(self.positions.keys()))

    def get_current_turn(self):
        return self.turn_order[self.current_turn_index]

    def move_player(self, role, to, transport):
        if role != self.get_current_turn():
            raise Exception("Not this player's turn.")
        self.players[role].move(to, transport)
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)

    def get_visible_positions(self):
        return {role: player.get_visible_position() for role, player in self.players.items()}

    def get_all_positions(self):
        return {role: player.position for role, player in self.players.items()}

    def get_history(self, role):
        return self.players[role].history if role in self.players else []
