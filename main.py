import os
import json
from InquirerPy import inquirer
from utils.clear import clear_screen
from core.character import Character


SAVE_DIR = "saves"


def ensure_save_dir():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def list_saved_characters():
    ensure_save_dir()
    files = [f[:-5] for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
    return files


def save_character(character: Character):
    ensure_save_dir()
    path = os.path.join(SAVE_DIR, f"{character.name}.json")
    with open(path, "w") as f:
        json.dump(character.to_dict(), f, indent=4)


def load_character(name: str) -> Character:
    path = os.path.join(SAVE_DIR, f"{name}.json")
    with open(path, "r") as f:
        data = json.load(f)
    return Character.from_dict(data)


def main():
    while True:  # loop the main menu
        clear_screen()
        print("=== D&D Assistant ===\n")

        menu0 = inquirer.select(
            message="Main Menu: ",
            choices=["Play Game", "Manage Characters", "Exit"],
        ).execute()

        match menu0:
            case "Play Game":
                clear_screen()
                print("Play Game not implemented yet.")
                input("\nPress Enter to return to menu...")

            case "Manage Characters":
                while True:  # loop the character manager
                    clear_screen()
                    menu2 = inquirer.select(
                        message="Character Manager: ",
                        choices=["Create New", "Edit Existing", "Back"],
                    ).execute()

                    match menu2:
                        case "Create New":
                            hero = Character.create_from_input()
                            save_character(hero)
                            clear_screen()
                            hero.summary()
                            input("\nSaved! Press Enter to return...")

                        case "Edit Existing":
                            names = list_saved_characters()
                            if not names:
                                clear_screen()
                                print("No saved characters found.")
                                input("\nPress Enter to return...")
                                continue

                            choice = inquirer.select(
                                message="Select Character to Edit:",
                                choices=names + ["Back"],
                            ).execute()

                            if choice == "Back":
                                continue

                            hero = load_character(choice)
                            while True:
                                clear_screen()
                                hero.summary()
                                print()
                                menu3 = inquirer.select(
                                    message=f"What do with {hero.name}?",
                                    choices=["Level Up", "Delete", "Back"],
                                ).execute()

                                match menu3:
                                    case "Level Up":
                                        hero.level_up()
                                        save_character(hero)
                                        clear_screen()
                                        print(
                                            f"{hero.name} has levelled up to {hero.level}!"
                                        )
                                        hero.summary()
                                        input("\nPress Enter to return...")

                                    case "Delete":
                                        confirm = (
                                            inquirer.text(
                                                message=f"Type DELETE to confirm deletion of {hero.name} or anything else to cancel:"
                                            )
                                            .execute()
                                            .strip()
                                        )
                                        if confirm == "DELETE":
                                            path = os.path.join(
                                                SAVE_DIR, f"{hero.name}.json"
                                            )
                                            os.remove(path)
                                            clear_screen()
                                            print(f"{hero.name} deleted.")
                                            input("\nPress Enter to return...")
                                            break
                                        else:
                                            clear_screen()
                                            print("Deletion cancelled.")
                                            input("\nPress Enter to return...")

                                    case "Back":
                                        break

                        case "Back":
                            break  # go back to main menu

            case "Exit":
                clear_screen()
                break


if __name__ == "__main__":
    main()
