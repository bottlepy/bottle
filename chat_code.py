import random

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.inventory = []

    def attack(self, enemy):
        damage = random.randint(10, 20)
        enemy.health -= damage
        print(f"{self.name} attacks {enemy.name} for {damage} damage!")

    def use_item(self, item):
        if item in self.inventory:
            if item == "health potion":
                self.health += 20
                print(f"{self.name} uses a health potion and gains 20 health!")
                self.inventory.remove(item)
        else:
            print("You don't have that item!")

    def display_status(self):
        print(f"{self.name}'s Health: {self.health}")
        print(f"{self.name}'s Inventory: {self.inventory}")

class Enemy:
    def __init__(self, name):
        self.name = name
        self.health = 50

    def attack(self, player):
        damage = random.randint(5, 15)
        player.health -= damage
        print(f"{self.name} attacks {player.name} for {damage} damage!")

# Creating player and enemy instances
player_name = input("Enter your name: ")
player = Player(player_name)
enemy = Enemy("Goblin")

# Game loop
while player.health > 0 and enemy.health > 0:
    action = input("Would you like to (a)ttack, (u)se item, or (q)uit? ")
    
    if action == "a":
        player.attack(enemy)
        enemy.attack(player)
    elif action == "u":
        item_to_use = input("Enter item to use: ")
        player.use_item(item_to_use)
        enemy.attack(player)
    elif action == "q":
        print("Goodbye!")
        break
    else:
        print("Invalid action!")

    player.display_status()
    print("")

if player.health <= 0:
    print("You were defeated! Game over.")
elif enemy.health <= 0:
    print("You defeated the enemy! Victory!")
