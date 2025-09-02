# run.py
from utils.clear import clear_screen

from core.character import Character

# from utils.abilities import Abilities


def main():
    clear_screen()
    print("=== D&D Character Builder ===\n")

    hero = Character.create_from_input()

    clear_screen()
    hero.summary()


if __name__ == "__main__":
    main()
