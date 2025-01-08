import socket
import threading
import random

# Constants
MAX_PLAYERS = 2
PORT = 9999
HOST = "0.0.0.0"

# Game state
players = []
turn_index = 0
game_over = False

# Function to broadcast messages to all clients
def broadcast(message):
    for player in players[:]:  # Iterate over a copy of the list
        try:
            print(f"Broadcasting to {player['name']}: {message}")  # Debug log
            player["socket"].sendall((message + "\n").encode())
        except BrokenPipeError:
            print(f"Player {player['name']} disconnected. Removing from the game.")
            players.remove(player)

# Function to handle a player's turn
def handle_turn(player, player_index):
    global turn_index, game_over

    # Check if it's the player's turn
    if turn_index != player_index:
        player["socket"].sendall("It's not your turn. Please wait...\n".encode())
        return

    # Prompt player for action
    player["socket"].sendall("Your turn! Choose [explore], [rest], or [quit]: ".encode())
    action = player["socket"].recv(1024).decode().strip().lower()
    print(f"Action received from {player['name']}: {action}")  # Debug log

    # Handle actions
    if action in ["explore", "e"]:
        print(f"Processing explore action for {player['name']}...")  # Debug log
        event = random.choice(["gold", "enemy", "trap"])
        if event == "gold":
            gold_found = random.randint(5, 20)
            player["gold"] += gold_found
            result = f"You found {gold_found} gold!"
        elif event == "enemy":
            damage = random.randint(5, 15)
            player["health"] -= damage
            result = f"You encountered an enemy and took {damage} damage!"
        elif event == "trap":
            damage = random.randint(10, 20)
            player["health"] -= damage
            result = f"You fell into a trap and took {damage} damage!"
        print(f"Result for {player['name']}: {result}")  # Debug log
        player["socket"].sendall(result.encode())  # Send result to current player
        broadcast(f"{player['name']} explored: {result}")
    elif action in ["rest", "r"]:
        heal = random.randint(5, 15)
        player["health"] = min(100, player["health"] + heal)
        result = f"You rested and healed {heal} health."
        player["socket"].sendall(result.encode())  # Send result to current player
        broadcast(f"{player['name']} rested: {result}")
    elif action in ["quit", "q"]:
        broadcast(f"{player['name']} has quit the game!")
        game_over = True
        return
    else:
        player["socket"].sendall("Invalid action. Turn skipped.\n".encode())
        return

    # Broadcast player stats after each turn
    broadcast(f"{player['name']} - Health: {player['health']}, Gold: {player['gold']}")

    # Check for win/loss conditions
    if player["gold"] >= 100:
        broadcast(f"{player['name']} has won the game with 100 gold!")
        game_over = True
    elif player["health"] <= 0:
        broadcast(f"{player['name']} has been defeated!")
        game_over = True

    # Move to the next player's turn
    turn_index = (turn_index + 1) % len(players)

# Function to handle a player's connection
def handle_player(player, player_index):
    global game_over

    try:
        player["socket"].sendall(f"Welcome, {player['name']}! Waiting for other players...\n".encode())

        # Wait for all players to join
        while len(players) < MAX_PLAYERS:
            pass

        broadcast("All players have joined. The game begins!")

        # Game loop
        while not game_over:
            handle_turn(player, player_index)

    except (BrokenPipeError, ConnectionResetError):
        print(f"Player {player['name']} disconnected.")
        players.remove(player)  # Remove the disconnected player
        broadcast(f"{player['name']} has left the game.")
        game_over = True  # Optionally end the game if a player disconnects
    finally:
        player["socket"].close()

# Main server function
def main_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_PLAYERS)
    print(f"Server running on {HOST}:{PORT}... Waiting for players to join.")

    while len(players) < MAX_PLAYERS:
        client_socket, addr = server.accept()
        client_socket.sendall("Enter your name: ".encode())
        name = client_socket.recv(1024).decode().strip()
        players.append({"socket": client_socket, "name": name, "health": 100, "gold": 0})
        print(f"Player {name} connected from {addr}")
        broadcast(f"{name} has joined the game!")

    # Start a thread for each player
    for i, player in enumerate(players):
        threading.Thread(target=handle_player, args=(player, i), daemon=True).start()

    while not game_over:
        pass  # Keep the server running until the game ends

    print("Game Over! Closing server.")
    server.close()

if __name__ == "__main__":
    main_server()

