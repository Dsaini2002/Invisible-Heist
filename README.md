
# 🕵️ Invisible Heist – Multiplayer Strategy Game

**Invisible Heist** is a Python-based multiplayer strategy game inspired by the classic board game *Scotland Yard*. 
Players take the roles of detectives and the elusive Mr. X in a tactical chase across a virtual city map.

---

## 🚀 How to Run

### 1. Start the Server

```bash
python multiplayer/server.py
```

- When prompted, input the number of detectives (excluding Mr. X).

### 2. Start the Clients (Players)

Each player runs:

```bash
python multiplayer/client.py
```

- A popup window will ask for the server's IP address.
- One player becomes **Mr. X** and must run their client **first**.
- Remaining players act as **Detectives**.

> ⚠️ The map interface will not appear for any player until **all players are connected and ready**.

---

## 🎮 Game Overview

- Turn-based strategy chase game with real-time updates.
- Detectives collaborate to capture Mr. X.
- Mr. X’s location remains hidden except at specific intervals.

---

## 🧰 Tech Stack

- Python
- pygame
- socket
- matplotlib
- PIL

---

## 📁 Project Structure

```
game/         → Core game logic and classes
map/          → Map visuals, graph logic, and plotting
multiplayer/  → Server and client networking code
main.py       → (Optional) Launcher or testing entry
```
