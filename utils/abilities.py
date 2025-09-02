from InquirerPy import inquirer
from .dice import roll_ability


class Abilities:
    def __init__(
        self, strength, dexterity, constitution, intelligence, wisdom, charisma
    ):
        self.strength = int(strength)
        self.dexterity = int(dexterity)
        self.constitution = int(constitution)
        self.intelligence = int(intelligence)
        self.wisdom = int(wisdom)
        self.charisma = int(charisma)

    @staticmethod
    def modifier(score):
        """Return the D&D ability modifier for a given score."""
        return (score - 10) // 2

    @classmethod
    def roll(cls):
        """Roll and assign ability scores interactively."""
        scores = [roll_ability() for _ in range(6)]
        scores.sort(reverse=True)
        print(f"\nRolled scores (descending): {scores}")
        assigned = {}
        abilities = [
            "Strength",
            "Dexterity",
            "Constitution",
            "Intelligence",
            "Wisdom",
            "Charisma",
        ]
        for ability in abilities:
            val = inquirer.select(
                message=f"Assign a value to {ability}:",
                choices=[str(s) for s in scores],
            ).execute()
            val = int(val)
            scores.remove(val)
            assigned[ability] = val
        return cls(
            assigned["Strength"],
            assigned["Dexterity"],
            assigned["Constitution"],
            assigned["Intelligence"],
            assigned["Wisdom"],
            assigned["Charisma"],
        )

    def apply_racial_bonuses(self, race, races_data):
        """Apply racial bonuses to abilities from data dict."""
        bonuses = races_data[race].get("bonuses", {})

        for ability, bonus in bonuses.items():
            if ability == "Other":
                # Restrict flexible bonuses to abilities without fixed bonuses
                fixed_bonuses = {ab for ab in bonuses if ab != "Other"}
                available = [
                    "Strength",
                    "Dexterity",
                    "Constitution",
                    "Intelligence",
                    "Wisdom",
                    "Charisma",
                ]
                available = [ab for ab in available if ab not in fixed_bonuses]

                chosen = []
                for i, amount in enumerate(bonus):
                    choice = inquirer.select(
                        message=f"Select ability score #{i+1} to give +{amount}:",
                        choices=[ab for ab in available if ab not in chosen],
                    ).execute()
                    current = getattr(self, choice.lower())
                    setattr(self, choice.lower(), current + amount)
                    chosen.append(choice)
            else:
                current = getattr(self, ability.lower())
                setattr(self, ability.lower(), current + bonus)

        if bonuses:
            print(f"\nApplied racial bonuses for {race}: {bonuses}")

    def as_dict(self):
        return {
            "Strength": self.strength,
            "Dexterity": self.dexterity,
            "Constitution": self.constitution,
            "Intelligence": self.intelligence,
            "Wisdom": self.wisdom,
            "Charisma": self.charisma,
        }
