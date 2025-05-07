import socket
import pickle
import threading
import time
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import traceback
import sys
sys.path.append('.')
sys.path.append('..')
from Game.game_logic import Game
# from game_components import Player, MrX, Detective, Graphical_map, get_routes, get_locations, MAPSIZE
    
class GameServer:
    def __init__(self, host='0.0.0.0', port=5555, num_detectives = 4):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.game = None
        self.clients = {}  # {connection: player_role}
        self.connections = []
        self.ready_count = 0
        self.turn_lock = threading.Lock()
        self.is_game_full = False
        self.game_started = False
        self.turn_count = 0
        self.max_detectives = num_detectives
        
        print(f"Server started on {host}:{port}")
        
    def start(self):
        """Start the server and listen for connections."""
        self.server.listen(10)
        print("Waiting for connections...")
        
        # Accept connections in a separate thread
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()
        
        try:
            while True:
                # Main server loop
                if self.game_started and self.game:
                    if self.game.check_game_over():
                        self.broadcast_game_over()
                        time.sleep(5)
                        self.reset_game()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Server shutting down...")
            self.server.close()
    
    def accept_connections(self):
        """Accept new client connections."""
        while not self.is_game_full:
            try:
                conn, addr = self.server.accept()
                self.connections.append(conn)
                print(f"New connection from {addr}")
                
                # Start a thread to handle this client
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
                time.sleep(1)  # Small delay to avoid overwhelming the server
                print(self.is_game_full)
            except Exception as e:
                print(f"Error accepting connection: {e}")
                break
        
        print("Game is full, no more connections accepted.")
        time.sleep(2)

        if self.ready_count == len(self.clients):
            print("Starting game...")
            self.start_game()
    
    def handle_client(self, conn, addr):
        """Handle communication with a client."""
        try:
            # Handle client messages
            while True:
                try:
                    header = conn.recv(4)
                    if not header:
                        break
                    msg_length = int.from_bytes(header, byteorder='big')
                    data = conn.recv(msg_length)
                    if not data:
                        break
                    msg = pickle.loads(data)
                    self.process_client_message(conn, msg)
                except (EOFError, ConnectionResetError, ConnectionAbortedError) as e:
                    print(f"Connection closed: {e}")
                    traceback.print_exc()
                    break
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    break
                
        except Exception as e:
            print(f"Error handling client {addr}: {e}")

    def process_client_message(self, conn, msg):
        """Process messages from clients."""
        if msg["type"] == "join":
                print("recieved message 'join'!")
                # Assign a role to the player
                role = self.assign_role()
                if role:
                    self.clients[conn] = role
                    self.send_to_client(conn, {"type": "role_assigned", "role": role})
                    print(f"Assigned role {role}!")
                    print(len(self.game.detectives))
                    if len(self.clients) == len(self.game.detectives) + 1 and len(self.clients) > 1:
                        print("game is full")
                        self.is_game_full = True
                else:
                    # No roles left
                    self.send_to_client(conn, {"type": "error", "message": "Game is full"})
                    self.is_game_full = True
                    conn.close()
                    self.connections.remove(conn)
                    return
                

        elif msg["type"] == "ready":
            print("message 'ready' received")
            with self.turn_lock:
                self.ready_count += 1
                print(f"Player {self.clients[conn]} is ready. Ready count: {self.ready_count}")
                
                # If all players are ready, start the game
        
        elif msg["type"] == "move" and self.game_started:
            print("message 'move' received")
            role = self.clients[conn]
            current_player = self.game.get_current_player()
            
            # Map client role to player object
            player_role = current_player.role
            
            # Check if it's this player's turn
            if player_role == role or (role == "Mr. X" and player_role == self.game.mr_x.role) or \
               (role.startswith("D") and player_role == role):
                dest = msg["destination"]
                transport = msg["transport"]
                
                # Apply the move
                with self.turn_lock:

                    valid_move = self.game.move_player(current_player, dest, transport)
                    if valid_move:
                        print(f"{player_role} moved to {dest} using {transport}")
                        # Update clients with new game state
                        self.broadcast_game_state()
                        
                        # Move to next turn
                        self.turn_count += 1

            else:
                print(f"Not {role}'s turn to move. Current player is {player_role}.")
    
    def assign_role(self):
        """Assign a role to a new player."""
        if not self.game:
            # Initialize game
            self.game = Game(self.max_detectives)
        
        # Possible roles: Mr. X or Detectives
        available_roles = []
        
        # Check if Mr. X is available
        mr_x_assigned = False
        for role in self.clients.values():
            if role == "Mr. X":
                mr_x_assigned = True
                break
        
        if not mr_x_assigned:
            available_roles.append("Mr. X")

        
        # Check which detectives are available
        for i in range(len(self.game.detectives)):
            detective_role = f"D{i+1}"
            if detective_role not in self.clients.values():
                available_roles.append(detective_role)
        
        if available_roles:
            return available_roles[0]
        return None
    
    def start_game(self):
        """Start the game once all players are ready."""
        print("All players ready, starting game")
        self.game_started = True
        self.turn_count = 0
        
        # Reset turn index to make sure we start with Mr. X
        self.game.turn_index = 0
        
        # Broadcast initial game state
        self.broadcast_game_state()
    
    def broadcast_game_state(self):
        """Send current game state to all clients."""
        print("Broadcasting game state")
        # Get visible state for all players
        visible_state = self.game.get_visible_state()
        
        current_player = self.game.get_current_player()
        current_player_role = current_player.role
        
        # Convert to client-friendly format
        if current_player_role == self.game.mr_x.role:
            current_player_role = "Mr. X"
        elif current_player_role.startswith("Detective"):
            # Convert "Detective D1" to "D1"
            current_player_role = current_player_role.split(" ")[1]
        
        possible_moves = self.game.get_possible_moves(current_player)
        
        game_state = {
            "type": "game_state",
            "turn_count": self.turn_count,
            "current_player": current_player_role,
            "visible_state": visible_state,
            "possible_moves": possible_moves,
            "is_mr_x_revealed": self.game.is_MrX_revealed,
            "is_game_over": self.game.is_game_over
        }
        
        # Send game state to all clients
        print(len(self.connections))
        for conn in self.connections:
            # Personalize game state based on player role
            player_role = self.clients.get(conn)
            personalized_state = self.personalize_game_state(game_state.copy(), player_role)
            self.send_to_client(conn, personalized_state)
    
    def personalize_game_state(self, game_state, player_role):
        """Customize game state based on player role."""
        # If player is Mr. X, they should see all positions
        game_state["role"] = player_role
        if player_role != "Mr. X":
            # Mr. X sees everything
            game_state["visible_state"]["mr_x_position"] = None
        
        return game_state
    
    def broadcast_game_over(self):
        """Broadcast game over message to all clients."""
        result = "Detectives win!" if self.game.is_MrX_revealed else "Mr. X escapes!"
        game_over_msg = {
            "type": "game_over",
            "result": result
        }
        self.broadcast(game_over_msg)
    
    def broadcast(self, message):
        """Send a message to all connected clients with header."""
        data = pickle.dumps(message)
        length = len(data).to_bytes(4, byteorder='big')
        for conn in self.connections:
            try:
                conn.sendall(length + data)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")

    
    def send_to_client(self, conn, message):
        """Send a message to a specific client."""
        try:
            # print("sending message to client", message)
            data = pickle.dumps(message)
            length = len(data).to_bytes(4, byteorder='big')
            conn.sendall(length + data)
            # print("Message sent to client")
        except Exception as e:
            print(f"Error sending to client: {e}")
    
    def reset_game(self):
        """Reset the game after it ends."""
        self.game = Game()
        self.game_started = False
        self.ready_count = 0
        self.turn_count = 0
        
        # Inform clients about reset
        reset_msg = {"type": "game_reset"}
        self.broadcast(reset_msg)

if __name__ == "__main__":
    num_detectives = int(input("Enter number of detectives in the game: "))
    server = GameServer(num_detectives=num_detectives)
    server.start()