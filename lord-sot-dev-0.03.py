import random
import time

# Constants for game balance
MAX_HEALTH = 100
GOLD_REWARD_RANGE = (5, 20)
HEAL_RANGE = (5, 15)
ENABLE_SLEEP = True

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'

# Player class to keep track of player stats
class Player:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.health: int = MAX_HEALTH
        self.gold: int = 0
        self.strength: int = 10

    def attack(self) -> int:
        return random.randint(1, self.strength)

# Enemy class for combat
class Enemy:
    def __init__(self, name: str, health: int, strength: int) -> None:
        self.name: str = name
        self.health: int = health
        self.strength: int = strength

    def attack(self) -> int:
        return random.randint(1, self.strength)

# Helper function to apply damage
def apply_damage(attacker: Player | Enemy, defender: Player | Enemy) -> int:
    damage = attacker.attack()
    defender.health -= damage
    return damage

# Game functions
def battle(player: Player, enemy: Enemy) -> bool:
    print(f"{Colors.RED}A wild {enemy.name} appears!{Colors.RESET}")
    while player.health > 0 and enemy.health > 0:
        player_damage = apply_damage(player, enemy)
        print(f"{Colors.GREEN}You deal {player_damage} damage to the {enemy.name}.{Colors.RESET}")

        if enemy.health > 0:
            enemy_damage = apply_damage(enemy, player)
            print(f"{Colors.RED}The {enemy.name} retaliates, dealing {enemy_damage} damage to you!{Colors.RESET}")

        print(f"{Colors.CYAN}Your health: {player.health}, {enemy.name}'s health: {enemy.health}{Colors.RESET}")
        if ENABLE_SLEEP:
            time.sleep(1)

    if player.health <= 0:
        print(f"{Colors.RED}You have been defeated!{Colors.RESET}")
        return False
    else:
        gold_won = random.randint(*GOLD_REWARD_RANGE)
        player.gold += gold_won
        print(f"{Colors.YELLOW}You defeated the {enemy.name}! You gained {gold_won} gold.{Colors.RESET}")
        return True

def explore(player: Player) -> bool:
    def peaceful_meadow() -> bool:
        print(f"{Colors.GREEN}You find a peaceful meadow. Nothing happens.{Colors.RESET}")
        return True

    def ancient_ruin() -> bool:
        print(f"{Colors.YELLOW}You encounter an ancient ruin. +5 gold!{Colors.RESET}")
        player.gold += 5
        return True

    def goblin_encounter() -> bool:
        return battle(player, Enemy("Goblin", 30, 5))

    def trap() -> bool:
        print(f"{Colors.RED}You fall into a trap! -10 health.{Colors.RESET}")
        player.health -= 10
        return player.health > 0

    events = {
        "Peaceful Meadow": peaceful_meadow,
        "Ancient Ruin": ancient_ruin,
        "Goblin Encounter": goblin_encounter,
        "Trap": trap
    }

    event_name, event_func = random.choice(list(events.items()))
    print(f"{Colors.BOLD}You encounter: {event_name}{Colors.RESET}")
    return event_func()

# Main game loop
def main() -> None:
    print(f"{Colors.BLUE}Welcome to the Legend of the Python Dragon!{Colors.RESET}")
    player_name = input(f"{Colors.CYAN}What is your name, brave adventurer? {Colors.RESET}")
    player = Player(player_name)

    while player.health > 0:
        print(f"\n{Colors.YELLOW}Health: {player.health}, Gold: {player.gold}{Colors.RESET}")
        while True:
            action = input(f"{Colors.CYAN}Do you want to [explore], [rest], or [quit]? {Colors.RESET}").lower()
            if action in ['explore', 'rest', 'quit']:
                break
            else:
                print(f"{Colors.RED}Invalid action, please choose again.{Colors.RESET}")

        if action == 'explore':
            if not explore(player):
                break
        elif action == 'rest':
            heal = random.randint(*HEAL_RANGE)
            player.health = min(MAX_HEALTH, player.health + heal)
            print(f"{Colors.GREEN}You rest and heal {heal} health points.{Colors.RESET}")
        elif action == 'quit':
            print(f"{Colors.BLUE}Thanks for playing! Your legend ends here.{Colors.RESET}")
            break

        if player.gold >= 100:
            print(f"{Colors.BOLD}{Colors.YELLOW}Congratulations, {player.name}! You are now a wealthy adventurer!{Colors.RESET}")
            break

    print(f"{Colors.RED}Game Over! Your legend ends here.{Colors.RESET}")

if __name__ == "__main__":
    main()

