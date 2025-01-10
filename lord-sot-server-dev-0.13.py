import socket
import threading
import random
import time

# Constants for game balance
MAX_HEALTH = 100
GOLD_REWARD_RANGE = (5, 20)
HEAL_RANGE = (5, 15)
ENABLE_SLEEP = True
MAX_PLAYERS = 2
PORT = 9999
HOST = "0.0.0.0"

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'

# Game state
players = []
turn_index = 0
game_over = False

# Player class for combat logic
class Enemy:
    def __init__(self, name: str, health: int, strength: int) -> None:
        self.name: str = name
        self.health: int = health
        self.strength: int = strength

    def attack(self) -> int:
        return random.randint(1, self.strength)

# Function to broadcast messages to all clients
def broadcast(message):
    for player in players[:]:  # Iterate over a copy of the list
        try:
            player["socket"].sendall((message + "\n").encode())
        except BrokenPipeError:
            print(f"Player {player['name']} disconnected. Removing from the game.")
            players.remove(player)

# Function to apply damage
def apply_damage(attacker: Enemy | dict, defender: Enemy | dict) -> int:
    damage = random.randint(1, 10)  # Replace with attack logic if needed
    defender["health"] -= damage
    return damage

# Battle function
def battle(player: dict, enemy: Enemy) -> bool:
    broadcast(f"{Colors.RED}A wild {enemy.name} appears!{Colors.RESET}")
    while player["health"] > 0 and enemy.health > 0:
        player_damage = random.randint(1, 10)  # Replace with player attack logic
        enemy.health -= player_damage
        broadcast(f"{Colors.GREEN}{player['name']} deals {player_damage} damage to the {enemy.name}.{Colors.RESET}")

        if enemy.health > 0:
            enemy_damage = enemy.attack()
            player["health"] -= enemy_damage
            broadcast(f"{Colors.RED}The {enemy.name} retaliates, dealing {enemy_damage} damage to {player['name']}!{Colors.RESET}")

        broadcast(f"{Colors.CYAN}{player['name']}'s health: {player['health']}, {enemy.name}'s health: {enemy.health}{Colors.RESET}")
        if ENABLE_SLEEP:
            time.sleep(1)

    if player["health"] <= 0:
        broadcast(f"{Colors.RED}{player['name']} has been defeated!{Colors.RESET}")
        return False
    else:
        gold_won = random.randint(*GOLD_REWARD_RANGE)
        player["gold"] += gold_won
        broadcast(f"{Colors.YELLOW}{player['name']} defeated the {enemy.name} and gained {gold_won} gold.{Colors.RESET}")
        return True

# Explore function
def explore(player: dict) -> bool:
    def peaceful_meadow() -> bool:
        broadcast(f"{Colors.GREEN}{player['name']} finds a peaceful meadow. Nothing happens.{Colors.RESET}")
        return True

    def ancient_ruin() -> bool:
        broadcast(f"{Colors.YELLOW}{player['name']} encounters an ancient ruin and gains 5 gold!{Colors.RESET}")
        player["gold"] += 5
        return True

    def goblin_encounter() -> bool:
        return battle(player, Enemy("Goblin", 30, 5))

    def trap() -> bool:
        broadcast(f"{Colors.RED}{player['name']} falls into a trap and loses 10 health!{Colors.RESET}")
        player["health"] -= 10
        return player["health"] > 0

    events = {
        "Peaceful Meadow": peaceful_meadow,
        "Ancient Ruin": ancient_ruin,
        "Goblin Encounter": goblin_encounter,
        "Trap": trap
    }

    event_name, event_func = random.choice(list(events.items()))
    broadcast(f"{Colors.BOLD}{player['name']} encounters: {event_name}{Colors.RESET}")
    return event_func()

# Function to handle a player's turn
def handle_turn(player: dict, player_index: int):
    global turn_index, game_over

    # Notify the player if it's not their turn
    if turn_index != player_index:
        if not player.get("notified"):
            player["socket"].sendall("It's not your turn. Please wait...\n".encode())
            player["notified"] = True  # Set a flag to avoid repeated messages
        return
    else:
        player["notified"] = False  # Reset flag when it's their turn

    # Prompt player for action
    try:
        player["socket"].sendall("Your turn! Choose [explore], [rest], or [quit]: ".encode())
        player["socket"].settimeout(30)  # Set a timeout for input
        action = player["socket"].recv(1024).decode().strip().lower()
    except socket.timeout:
        broadcast(f"{player['name']} took too long and their turn is skipped.")
        action = "rest"  # Default action

    print(f"Action received from {player['name']}: {action}")

    # Handle actions
    if action in ["explore", "e"]:
        if not explore(player):
            game_over = True
    elif action in ["rest", "r"]:
        heal = random.randint(*HEAL_RANGE)
        player["health"] = min(MAX_HEALTH, player["health"] + heal)
        broadcast(f"{Colors.GREEN}{player['name']} rests and heals {heal} health points.{Colors.RESET}")
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
def handle_player(player: dict, player_index: int):
    global game_over

    try:
        player["socket"].sendall(f"{Colors.GREEN}Welcome, {player['name']}!{Colors.RESET}\n".encode())

        # Wait until all players have joined
        while len(players) < MAX_PLAYERS:
            player["socket"].sendall(f"{Colors.BLUE}Waiting for more players to join... ({len(players)}/{MAX_PLAYERS}){Colors.RESET}\n".encode())
            time.sleep(1)

        # Notify all players that the game has started
        if len(players) == MAX_PLAYERS:
            broadcast(f"{Colors.YELLOW}All players have joined. The game begins!{Colors.RESET}")

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
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.listen(MAX_PLAYERS)
    print(f"Server running on {HOST}:{PORT}... Waiting for players to join.")

    while len(players) < MAX_PLAYERS:
        client_socket, addr = server.accept()
        print(f"Connection received from {addr}")  # Debug log
        client_socket.sendall("Enter your name: ".encode())
        name = client_socket.recv(1024).decode().strip()[:20]  # Limit name length to 20
        if not name.isalnum():
            client_socket.sendall("Invalid name. Only alphanumeric characters are allowed.\n".encode())
            client_socket.close()
            continue
        print(f"Received name: {name}")  # Debug log
        players.append({"socket": client_socket, "name": name, "health": 100, "gold": 0})
        print(f"Player {name} added to the game.")  # Debug log
        broadcast(f"{name} has joined the game!")  # Broadcast the new player joining
        broadcast(f"{Colors.BLUE}Waiting for more players to join... ({len(players)}/{MAX_PLAYERS}){Colors.RESET}")

    broadcast(f"{Colors.YELLOW}All players have joined. The game begins!{Colors.RESET}")

    # Start a thread for each player
    for i, player in enumerate(players):
        threading.Thread(target=handle_player, args=(player, i), daemon=True).start()

    while not game_over:
        pass  # Keep the server running until the game ends

    print("Game Over! Closing server.")
    server.close()

if __name__ == "__main__":
    main_server()

