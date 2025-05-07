import sys
sys.path.append('.')
sys.path.append('..')

from Map.routes import get_routes, get_locations
from Map.graph import Graphical_map
import random
from Game.player import Player, MrX, Detective

SHOW_MRX_AFTER_TURNS = 3

class Game():
    def __init__(self, num_detectives=4):
        self.graph = Graphical_map(get_routes()).get_graph()
        self.positions = get_locations()
        self.is_game_over = False
        self.is_MrX_revealed = False
        self.server_view = False

        # Initialize players
        all_positions = list(self.positions.keys())
        random.shuffle(all_positions)

        self.players = []
        self.turn_index = 0

        # Create MrX
        self.mr_x = MrX(all_positions.pop())
        self.players.append(self.mr_x)

        # Create detectives
        self.detectives = []
        for i in range(num_detectives):
            det = Detective(f"D{i+1}", all_positions.pop())
            self.players.append(det)
            self.detectives.append(det)

    def get_current_player(self):
        player = self.players[self.turn_index]
        return player

    def get_possible_moves(self, player: Player):
        current = player.position
        neighbors = self.graph[current]
        moves = []

        for neighbor, edge_data in neighbors.items():
            transport_types = edge_data['transport']
            for transport in transport_types:
                if player.has_ticket(transport):
                    moves.append((neighbor, transport))

        return moves

    def move_player(self, player: Player, destination, transport):
        if (destination, transport) not in self.get_possible_moves(player):
            raise ValueError("Invalid move or no ticket available.")

        player.move(destination, transport)
        self.next_turn()
        return True

    def next_turn(self):
        self.turn_index = (self.turn_index + 1) % len(self.players)

    def get_visible_state(self):
        state = {
            'positions': {
                f"D{i+1}": det.get_visible_position() for i, det in enumerate(self.detectives)
            },
            'mr_x_position': self.mr_x.get_visible_position(),
            'turn': self.turn_index,
            'detectives_tickets': {
                f"D{i+1}": det.tickets for i, det in enumerate(self.detectives)
            },
            'mr_x_history': {
                'locations': self.mr_x.location_history,
                'transports': self.mr_x.transport_history
            }
        }
        return state
    
    def check_game_over(self):
        # Check if Mr. X is caught
        for det in self.detectives:
            if det.position == self.mr_x.position:
                print(f"Game Over! {det.role} caught Mr. X at {det.position}.")
                self.is_game_over = True
                self.is_MrX_revealed = True
                return True

        # Check if all detectives are stuck (no valid moves)
        stuck_detectives = 0
        for det in self.detectives:
            if not self.get_possible_moves(det):
                stuck_detectives += 1

        if stuck_detectives == len(self.detectives):
            print("Game Over! All detectives are stuck. Mr. X wins.")
            self.is_game_over = True
            return True

        return False