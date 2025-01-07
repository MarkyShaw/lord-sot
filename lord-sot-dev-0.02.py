import random
import time

# Constants for game balance
MAX_HEALTH = 100
GOLD_REWARD_RANGE = (5, 20)
HEAL_RANGE = (5, 15)
ENABLE_SLEEP = True

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
    print(f"A wild {enemy.name} appears!")
    while player.health > 0 and enemy.health > 0:
        player_damage = apply_damage(player, enemy)
        print(f"You deal {player_damage} damage to the {enemy.name}.")

        if enemy.health > 0:
            enemy_damage = apply_damage(enemy, player)
            print(f"The {enemy.name} retaliates, dealing {enemy_damage} damage to you!")

        print(f"Your health: {player.health}, {enemy.name}'s health: {enemy.health}")
        if ENABLE_SLEEP:
            time.sleep(1)

    if player.health <= 0:
        print("You have been defeated!")
        return False
    else:
        gold_won = random.randint(*GOLD_REWARD_RANGE)
        player.gold += gold_won
        print(f"You defeated the {enemy.name}! You gained {gold_won} gold.")
        return True

def explore(player: Player) -> bool:
    def peaceful_meadow() -> bool:
        print("You find a peaceful meadow. Nothing happens.")
        return True

    def ancient_ruin() -> bool:
        print("You encounter an ancient ruin. +5 gold!")
        player.gold += 5
        return True

    def goblin_encounter() -> bool:
        return battle(player, Enemy("Goblin", 30, 5))

    def trap() -> bool:
        print("You fall into a trap! -10 health.")
        player.health -= 10
        return player.health > 0

    events = {
        "Peaceful Meadow": peaceful_meadow,
        "Ancient Ruin": ancient_ruin,
        "Goblin Encounter": goblin_encounter,
        "Trap": trap
    }

    event_name, event_func = random.choice(list(events.items()))
    print(f"You encounter: {event_name}")
    return event_func()

# Main game loop
def main() -> None:
    print("Welcome to the Legend of the Python Dragon!")
    player_name = input("What is your name, brave adventurer? ")
    player = Player(player_name)

    while player.health > 0:
        print(f"\nHealth: {player.health}, Gold: {player.gold}")
        while True:
            action = input("Do you want to [explore], [rest], or [quit]? ").lower()
            if action in ['explore', 'rest', 'quit']:
                break
            else:
                print("Invalid action, please choose again.")

        if action == 'explore':
            if not explore(player):
                break
        elif action == 'rest':
            heal = random.randint(*HEAL_RANGE)
            player.health = min(MAX_HEALTH, player.health + heal)
            print(f"You rest and heal {heal} health points.")
        elif action == 'quit':
            print("Thanks for playing! Your legend ends here.")
            break

        if player.gold >= 100:
            print(f"Congratulations, {player.name}! You are now a wealthy adventurer!")
            break

    print("Game Over! Your legend ends here.")

if __name__ == "__main__":
    main()
