import random
import time

# Player class to keep track of player stats
class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.gold = 0
        self.strength = 10

    def attack(self):
        return random.randint(1, self.strength)

# Enemy class for combat
class Enemy:
    def __init__(self, name, health, strength):
        self.name = name
        self.health = health
        self.strength = strength

    def attack(self):
        return random.randint(1, self.strength)

# Game functions
def battle(player, enemy):
    print(f"A wild {enemy.name} appears!")
    while player.health > 0 and enemy.health > 0:
        player_damage = player.attack()
        enemy.health -= player_damage
        print(f"You deal {player_damage} damage to the {enemy.name}.")
        
        if enemy.health > 0:
            enemy_damage = enemy.attack()
            player.health -= enemy_damage
            print(f"The {enemy.name} retaliates, dealing {enemy_damage} damage to you!")
        
        print(f"Your health: {player.health}, {enemy.name}'s health: {enemy.health}")
        time.sleep(1)

    if player.health <= 0:
        print("You have been defeated!")
        return False
    else:
        gold_won = random.randint(5, 20)
        player.gold += gold_won
        print(f"You defeated the {enemy.name}! You gained {gold_won} gold.")
        return True

def explore(player):
    def peaceful_meadow():
        print("You find a peaceful meadow. Nothing happens.")
        return True

    def ancient_ruin():
        print("You encounter an ancient ruin. +5 gold!")
        player.gold += 5
        return True

    def goblin_encounter():
        return battle(player, Enemy("Goblin", 30, 5))

    def trap():
        print("You fall into a trap! -10 health.")
        player.health -= 10
        return player.health > 0

    events = [
        peaceful_meadow,
        ancient_ruin,
        goblin_encounter,
        trap
    ]
    event = random.choice(events)
    return event()

# Main game loop
def main():
    print("Welcome to the Legend of the Python Dragon!")
    player_name = input("What is your name, brave adventurer? ")
    player = Player(player_name)

    while player.health > 0:
        print(f"\nHealth: {player.health}, Gold: {player.gold}")
        action = input("Do you want to [explore] or [rest]? ").lower()

        if action == 'explore':
            if not explore(player):
                break
        elif action == 'rest':
            heal = random.randint(5, 15)
            player.health = min(100, player.health + heal)
            print(f"You rest and heal {heal} health points.")
        else:
            print("Invalid action, try again.")

    print("Game Over! Your legend ends here.")

if __name__ == "__main__":
    main()
