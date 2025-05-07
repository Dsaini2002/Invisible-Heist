import socket
import pickle
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox, simpledialog
import traceback
import sys
sys.path.append('.')
sys.path.append('..')
from Map.display import update_graph, get_move_popup

MAPSIZE = (2036, 1618)

class GameClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.role = None
        self.game_state = None
        self.connected = False
        self.running = True
        self.root = tk.Tk()
        self.root.withdraw()
        
        # GUI elements
        self.fig, self.ax = plt.subplots(figsize=(18, 12))
        
    def connect_to_server(self):
        """Connect to the game server."""
        try:
            self.client.connect((self.host, self.port))
            self.connected = True
            self.running = True

            # Send join request
            self.send_message({"type": "join"})

            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
            # Start receiving messages from server
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            return False
    
    def send_ready(self):
        """Send ready message to server with confirmation dialog."""
        if self.connected:            
            # Ask user if they're ready to start
            is_ready = messagebox.askyesno(
                "Ready to Play", 
                "Are you ready to start the game?",
                icon='question'
            )
            
            # If user confirmed they're ready, send the message
            if is_ready:
                self.send_message({"type": "ready"})
                return True
            
        return False
    
    def recv_all(self, sock, length):
        """Receive exactly `length` bytes from the socket."""
        data = b""
        print("trying to receive data of length ", length)
        while len(data) < length:
            more = sock.recv(length - len(data))
            if not more:
                raise EOFError("Socket closed before receiving all data")
            data += more
        return data

    def receive_messages(self):
        """Receive and process messages from server."""
        print("[Client] receive_messages() thread started!")
        while self.running and self.connected:
            try:
                header = self.client.recv(4)
                if not header:
                    print("Server closed connection.")
                    break

                msg_length = int.from_bytes(header, byteorder='big')
                if msg_length > 500:
                    break
                data = self.recv_all(self.client, msg_length)
                message = pickle.loads(data)
                print("message recieved!")
                self.process_server_message(message)
                
            except (EOFError, ConnectionResetError, ConnectionAbortedError) as e:
                print(f"Connection closed: {e}")
                break
            except Exception as e:
                print(f"Error receiving data: {e}")
                traceback.print_exc()
                break
    
    def process_server_message(self, message):
        """Process messages received from the server."""
        print("Processing message", message.get("type"))
        msg_type = message.get("type")
        
        if msg_type == "role_assigned":
            self.role = message.get("role")

        elif msg_type == "game_state":
            self.game_state = message
            if self.root:
                self.root.after(0, self.update_gui)
            else:
                self.update_gui()
            if self.role == self.game_state['current_player']:
                self.root.after(0, self.prompt_and_make_move)
            
        elif msg_type == "game_over":
            result = message.get("result")
            self.ax.text(MAPSIZE[0] / 2, MAPSIZE[1] / 2, result, fontsize=50, fontweight='bold', color='red', ha='center')
            
        print("message processed")

    def prompt_and_make_move(self):
        dest, transport = get_move_popup(self.game_state["possible_moves"], self.game_state["current_player"])
        self.make_move(dest, transport)
 
    def make_move(self, destination, transport, dialog=None):
        """Send a move to the server."""

        self.send_message({
            "type": "move",
            "destination": destination,
            "transport": transport
        })
            
    def send_message(self, message):
        """Send a message to the server."""
        if not self.connected:
            return
            
        try:
            data = pickle.dumps(message)
            length = len(data).to_bytes(4, byteorder='big')
            self.client.sendall(length + data)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.connected = False
    
    def update_gui(self):
        """Update the GUI periodically."""
        if self.running:
            # Any periodic updates can go here
            update_graph(self.game_state, self.ax) if self.game_state else None
    
    def on_closing(self):
        """Handle window closing."""
        self.running = False
        if self.connected:
            try:
                self.client.close()
            except:
                pass
        self.root.destroy()
    
    def run(self):
        self.root.withdraw()
        """Start the client."""
        self.root.mainloop()

if __name__ == "__main__":
    import sys
    
    # Check if server address was provided as argument
    if len(sys.argv) > 1:
        server_address = sys.argv[1]
    else:
        # Ask for server address
        server_address = simpledialog.askstring(
            "Server Address", 
            "Enter the server address:",
            initialvalue="localhost"
        )
    
    if server_address:
        client = GameClient(host=server_address)
        connected = client.connect_to_server()
        if connected:
            ready = client.send_ready()
            if ready:
                print("Ready to play!")
                plt.ion()
                plt.show()
                client.fig.canvas.mpl_connect("close_event", lambda event: client.on_closing())
                client.run()
            else:
                print("Failed to send ready status.")
        else:
            print("Failed to connect to the server.")
    else:
        print("No server address provided, exiting...")