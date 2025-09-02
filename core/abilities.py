from InquirerPy import inquirer
from utils.dice import roll_ability
from data.races import RACES


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
        return (score - 10) // 2

    @classmethod
    def roll(cls):
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

    def apply_racial_bonuses(self, race):
        bonuses = RACES[race].get("bonuses", {})

        for ability, bonus in bonuses.items():
            if ability == "Other":
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

    def _ability_choices(self, exclude=None):
        exclude = exclude or []
        abilities = [
            "Strength",
            "Dexterity",
            "Constitution",
            "Intelligence",
            "Wisdom",
            "Charisma",
        ]
        return [
            f"{ab} ({getattr(self, ab.lower())})"
            for ab in abilities
            if ab not in exclude
        ]

    def _parse_choice(self, choice):
        return choice.split()[0]

    def apply_asi(self, combat_stats, equipment):
        option = inquirer.select(
            message="Ability Score Improvement: choose type",
            choices=["Increase two abilities by +1", "Increase one ability by +2"],
        ).execute()

        if option == "Increase two abilities by +1":
            chosen = []
            for i in range(2):
                choice = inquirer.select(
                    message=f"Select ability #{i+1} to increase by +1:",
                    choices=self._ability_choices(exclude=chosen),
                ).execute()
                ability = self._parse_choice(choice)
                current = getattr(self, ability.lower())
                setattr(self, ability.lower(), min(current + 1, 20))
                chosen.append(ability)
        else:
            choice = inquirer.select(
                message="Select ability to increase by +2:",
                choices=self._ability_choices(),
            ).execute()
            ability = self._parse_choice(choice)
            current = getattr(self, ability.lower())
            setattr(self, ability.lower(), min(current + 2, 20))

        combat_stats.recalculate_hp()
        combat_stats.calculate_ac(equipment)

    def to_dict(self):
        return {
            "Strength": self.strength,
            "Dexterity": self.dexterity,
            "Constitution": self.constitution,
            "Intelligence": self.intelligence,
            "Wisdom": self.wisdom,
            "Charisma": self.charisma,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["Strength"],
            data["Dexterity"],
            data["Constitution"],
            data["Intelligence"],
            data["Wisdom"],
            data["Charisma"],
        )
