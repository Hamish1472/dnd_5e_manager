from .abilities import Abilities
from .combat import CombatStats
from .equipment import select_starting_equipment
from data.races import RACES
from data.classes import CLASSES
from InquirerPy import inquirer


class Character:
    def __init__(
        self,
        name,
        race,
        char_class,
        level,
        alignment,
        abilities,
        combat_stats,
        equipment,
    ):
        self.name = name
        self.race = race
        self.char_class = char_class
        self.level = int(level)
        self.alignment = alignment
        self.abilities = abilities
        self.combat_stats = combat_stats
        self.equipment = equipment

    ASI_LEVELS = {
        "Default": [4, 8, 12, 16, 19],
        "Fighter": [4, 6, 8, 12, 14, 16, 19],
        "Rogue": [4, 8, 10, 12, 16, 19],
    }

    def summary(self):
        print("=== Character Summary ===")
        print(f"Name: {self.name}")
        print(f"Race: {self.race}")
        print(f"Class: {self.char_class}")
        print(f"Level: {self.level}")
        # print(f"Background: {self.background}\n")

        print("\n--- Abilities ---")
        for ability, score in self.abilities.to_dict().items():
            mod = Abilities.modifier(score)
            sign = "+" if mod >= 0 else ""
            print(f"{ability}: {score} ({sign}{mod})")

        print("\n--- Combat Stats ---")
        self.combat_stats.calculate_ac(self.equipment)
        cs = self.combat_stats
        ac_display = (
            f"{cs.ac} (with shield {cs.ac_with_shield})"
            if cs.ac_with_shield
            else f"{cs.ac}"
        )
        print(f"  AC: {ac_display}")
        print(f"  Initiative: {cs.initiative:+}")
        print(f"  Speed: {cs.speed}")

        print("\nHit Points:")
        print(f"  Max HP: {cs.hp_max}")
        print(f"  Current HP: {cs.hp_current}")
        print(f"  Temp HP: {cs.hp_temp}")

        print("\nHit Dice:")
        print(f"  Type: d{cs.hit_die}")
        # Placeholder until we add short-rest mechanics
        hit_dice_remaining = cs.level
        print(f"  Remaining: {hit_dice_remaining}/{cs.level}")

        print("\nDeath Saves:")
        # Placeholders until tracking is added
        print("  Successes: 0")
        print("  Failures: 0")

        print("\n--- Equipment ---")
        counted = {}
        for item in self.equipment:
            counted[item] = counted.get(item, 0) + 1
        for item, qty in counted.items():
            if qty > 1:
                print(f"- {item} (x{qty})")
            else:
                print(f"- {item}")

    @classmethod
    def create_from_input(cls):
        name = input("Character Name: ")

        race = inquirer.select(
            message="Select Race:", choices=list(RACES.keys())
        ).execute()

        classes = [
            "Barbarian",
            "Bard",
            "Cleric",
            "Druid",
            "Fighter",
            "Monk",
            "Paladin",
            "Ranger",
            "Rogue",
            "Sorcerer",
            "Warlock",
            "Wizard",
        ]
        char_class = inquirer.select(message="Select Class:", choices=classes).execute()

        level = inquirer.select(message="Level: ", choices=list(range(1, 21))).execute()

        alignments = [
            "Lawful Good",
            "Lawful Neutral",
            "Lawful Evil",
            "Neutral Good",
            "True Neutral",
            "Neutral Evil",
            "Chaotic Good",
            "Chaotic Neutral",
            "Chaotic Evil",
        ]
        alignment = inquirer.select(message="Alignment: ", choices=alignments).execute()

        roll_choice = inquirer.select(
            message="Roll or manual ability scores?",
            choices=["Roll", "Manual"],
        ).execute()

        match roll_choice:
            case "Roll":
                abilities = Abilities.roll()
                abilities.apply_racial_bonuses(race)
                hit_die = CLASSES[char_class]["hit_die"]
                equipment = select_starting_equipment(char_class)
                combat_stats = CombatStats(
                    level=level,
                    hit_die=hit_die,
                    abilities=abilities,
                    speed=RACES[race]["speed"],
                    proficiency_bonus=2 + ((level - 1) // 4),
                    char_class=char_class,
                )
                for asi_level in cls.ASI_LEVELS.get(
                    char_class, cls.ASI_LEVELS["Default"]
                ):
                    if level >= asi_level:
                        abilities.apply_asi(combat_stats, equipment)

            case "Manual":
                scores = {}
                for ab in [
                    "Strength",
                    "Dexterity",
                    "Constitution",
                    "Intelligence",
                    "Wisdom",
                    "Charisma",
                ]:
                    scores[ab] = int(input(f"{ab}: "))
                abilities = Abilities(**{k.lower(): v for k, v in scores.items()})
                hit_die = CLASSES[char_class]["hit_die"]
                equipment = select_starting_equipment(char_class)
                combat_stats = CombatStats(
                    level=level,
                    hit_die=hit_die,
                    abilities=abilities,
                    speed=RACES[race]["speed"],
                    proficiency_bonus=2 + ((level - 1) // 4),
                    char_class=char_class,
                )

        return cls(
            name, race, char_class, level, alignment, abilities, combat_stats, equipment
        )

    def level_up(self):
        self.level += 1
        self.combat_stats.level_up()

        # Select correct ASI table
        asi_levels = self.ASI_LEVELS.get(self.char_class, self.ASI_LEVELS["Default"])
        if self.level in asi_levels:
            self.abilities.apply_asi(self.combat_stats, self.equipment)

    def to_dict(self):
        return {
            "name": self.name,
            "race": self.race,
            "char_class": self.char_class,
            "level": self.level,
            "alignment": self.alignment,
            "abilities": self.abilities.to_dict(),
            "combat_stats": self.combat_stats.to_dict(),
            "equipment": self.equipment,
        }

    @classmethod
    def from_dict(cls, data):
        abilities = Abilities.from_dict(data["abilities"])
        combat_stats = CombatStats.from_dict(data["combat_stats"], abilities)
        return cls(
            name=data["name"],
            race=data["race"],
            char_class=data["char_class"],
            level=data["level"],
            alignment=data.get("alignment", "True Neutral"),
            abilities=abilities,
            combat_stats=combat_stats,
            equipment=data.get("equipment", []),
        )
