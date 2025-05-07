import time
import sys
import matplotlib.pyplot as plt

sys.path.append('.')
sys.path.append('..')

from Game.game_logic import Game
from Map.display import update_graph, get_move_popup

def run_game(game: Game):
    turn_count = 0
    fig, ax = plt.subplots(figsize=(18, 12))
    plt.ion()

    while not game.check_game_over():
        # update_graph(game, ax, turn_count)
        if turn_count > 0:
            current_player = game.get_current_player()
            # print(f"\nTurn {turn_count} — {current_player.role}'s move")

            # Get possible moves
            possible_moves = game.get_possible_moves(current_player)
            if not possible_moves:
                print(f"{current_player.role} has no possible moves! Skipping turn.")
                continue
            
            dest, transport = get_move_popup(possible_moves, current_player.role)

            # Apply the move
            game.move_player(current_player, dest, transport)
            print(f"{current_player.role} moved to {dest} using {transport}")

        # Update graph
        update_graph(game, ax, turn_count)
        plt.pause(0.5)

        # Advance to next turn
        turn_count += 1

    print("\nGame Over!")
    update_graph(game, ax, turn_count)
    plt.pause(2)  # Pause to show final state
    if game.is_game_over:
        if game.is_MrX_revealed:
            print("Mr. X is caught!")
        else:
            print("Mr. X escaped!")
    # plt.ioff()
    plt.show()