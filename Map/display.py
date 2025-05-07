import matplotlib.pyplot as plt
import networkx as nx
import sys
sys.path.append('.')
sys.path.append('..')
from Game.game_logic import SHOW_MRX_AFTER_TURNS, Game
from Map.routes import MAPSIZE, get_locations
import tkinter as tk
from tkinter import messagebox
import matplotlib.patches as mpatches


def get_move_popup(possible_moves, player_name):
    selected_move = None  # Will hold the result

    def on_submit(event=None):
        nonlocal selected_move
        choice = entry.get()
        if not choice.isdigit():
            messagebox.showerror("Invalid input", "Please enter a number.", parent=popup)
            return
        index = int(choice) - 1
        if 0 <= index < len(possible_moves):
            selected_move = possible_moves[index]
            popup.destroy()
        else:
            messagebox.showerror("Invalid choice", "Move number out of range.", parent=popup)

    # root = tk.Tk()
    # root.withdraw()  # Hide root window

    popup = tk.Toplevel()
    popup.title("Player Move")
    popup.geometry("+0+100")  # Extreme left of screen

    move_text = f"{player_name}, choose your move:\n"
    for i, (station, transport) in enumerate(possible_moves):
        move_text += f"{i+1}. Station {station} via {transport}\n"

    label = tk.Label(popup, text=move_text, justify='left', font=('Arial', 10))
    label.pack(padx=10, pady=10)

    entry = tk.Entry(popup, width=10)
    entry.pack(padx=10)
    entry.bind("<Return>", on_submit)  # Submit on Enter
    entry.focus()

    popup.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent accidental close
    popup.grab_set()  # Make the popup modal
    popup.wait_window()  # Wait until popup is destroyed

    return selected_move


def update_graph(game_state, ax, turn_count=0):
    ax.clear()

    # Load background map
    img = plt.imread('./Map/map.jpg')
    ax.imshow(img, extent=[0, MAPSIZE[0], 0, MAPSIZE[1]])

    positions = get_locations()

    # Get current visible state
    visible_state = game_state['visible_state']
    detectives_positions = visible_state['positions']
    mr_x_position = visible_state['mr_x_position']

    # Colors
    detective_colors = ['blue', 'green', 'orange', 'purple', 'cyan', 'brown']
    mr_x_color = 'red'

    # Plot detectives
    for i, (_, pos) in enumerate(detectives_positions.items()):
        if pos:
            color = detective_colors[i % len(detective_colors)]
            ax.scatter(positions[pos][0], positions[pos][1], s=200, color=color, edgecolors='black', linewidths=3, zorder=3)
            # ax.text(positions[pos][0], positions[pos][1] + 15, detective, color="black", fontsize=10, ha='center')

    # Plot Mr. X if visible
    if game_state['visible_state']['mr_x_position']:
        ax.scatter(positions[mr_x_position][0], positions[mr_x_position][1], s=200, color=mr_x_color, edgecolors='black', linewidths=3, zorder=3)
        # ax.text(positions[mr_x_position][0], positions[mr_x_position][1] + 15, 'MrX', color="black", fontsize=10, ha='center')

    # Mr. X History (right side of map)
    locs = game_state['visible_state']['mr_x_history']['locations']
    trans = game_state['visible_state']['mr_x_history']['transports']
    table_data = [(str(l) if l != -1 else "Hidden", t) for l, t in zip(locs, trans)]

    # Start X and Y for the table (place it to the right of the map)
    table_x = MAPSIZE[0] + 100
    table_y = MAPSIZE[1] - 250
    ax.text(table_x + 40, table_y + 20, "Mr. X History", fontsize=16, fontweight='bold', ha='left')
    # ax.text(table_x, table_y - 40, "Location, Transport", fontsize=14, fontweight='bold', ha='left')
    for i, (loc, t) in enumerate(table_data[-6:]):  # show last 6
        ax.text(table_x, table_y - 50 * (i + 3), f"{i+1}. {loc}, {t}", fontsize=12, ha='left')

    # Legend (outside top-right)
    legend_patches = []
    for i, (det, _) in enumerate(detectives_positions.items()):
        color = detective_colors[i % len(detective_colors)]
        patch = mpatches.Patch(color=color, label=det)
        legend_patches.append(patch)

    if game_state["is_game_over"]:
        if game_state["is_MrX_revealed"]:
            ax.text(MAPSIZE[0] / 2, MAPSIZE[1] / 2, "Mr. X Caught!", fontsize=50, fontweight='bold', color='red', ha='center')
        else:
            ax.text(MAPSIZE[0] / 2, MAPSIZE[1] / 2, "Mr. X Escaped!", fontsize=50, fontweight='bold', color='green', ha='center')
    
    ax.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0., title='Detectives')

    # Adjust layout
    ax.set_title(f"Scotland Yard | Role: {game_state['role']}")
    ax.set_xlim(0, MAPSIZE[0] + 150)  # Extra space on right
    ax.set_ylim(0, MAPSIZE[1] + 100)  # Slight space at top
    ax.axis('off')

    plt.tight_layout()
    plt.draw()
