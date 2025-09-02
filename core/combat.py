from .abilities import Abilities
from data.armours import ARMOURS
import random


class CombatStats:
    def __init__(
        self,
        level,
        hit_die,
        abilities,
        speed,
        proficiency_bonus,
        char_class=None,
        hp_rolls=None,
        hp_current=None,
    ):
        self.level = int(level)
        self.hit_die = int(hit_die)
        self.abilities = abilities
        self.speed = int(speed)
        self.proficiency_bonus = int(proficiency_bonus)
        self.char_class = char_class

        self.hp_rolls = hp_rolls or [
            random.randint(1, hit_die) for _ in range(1, level)
        ]

        self.hp_max = 0
        self.hp_current = hp_current if hp_current is not None else 0
        self.hp_temp = 0

        self.initiative = Abilities.modifier(abilities.dexterity) if abilities else 0

        self.recalculate_hp()
        # AC will be computed with equipment passed from Character
        self.ac = 0
        self.ac_with_shield = None

    def recalculate_hp(self):
        con_mod = (
            Abilities.modifier(self.abilities.constitution) if self.abilities else 0
        )

        hp_max = self.hit_die + con_mod
        for roll in self.hp_rolls:
            hp_max += roll + con_mod

        if self.hp_current == 0:
            self.hp_current = hp_max
        else:
            ratio = self.hp_current / self.hp_max if self.hp_max > 0 else 1
            self.hp_current = max(1, int(hp_max * ratio))

        self.hp_max = hp_max

    def calculate_ac(self, equipment):
        dex_mod = Abilities.modifier(self.abilities.dexterity) if self.abilities else 0
        con_mod = (
            Abilities.modifier(self.abilities.constitution) if self.abilities else 0
        )
        wis_mod = Abilities.modifier(self.abilities.wisdom) if self.abilities else 0

        base_ac = 10
        ac_with_shield = None

        armour_item = next(
            (
                item
                for item in equipment
                if item in ARMOURS and ARMOURS[item]["type"] == "base"
            ),
            None,
        )

        if armour_item:
            armour_data = ARMOURS[armour_item]
            base_ac = armour_data["base_ac"]
            if armour_data["dex_mod"]:
                if armour_data["max_dex_mod"] is not None:
                    base_ac += min(dex_mod, armour_data["max_dex_mod"])
                else:
                    base_ac += dex_mod
        else:
            if self.char_class == "Barbarian":
                base_ac = 10 + dex_mod + con_mod
            elif self.char_class == "Monk":
                base_ac = 10 + dex_mod + wis_mod
            else:
                base_ac = 10 + dex_mod

        if "Shield" in equipment:
            ac_with_shield = base_ac + ARMOURS["Shield"]["bonus"]

        self.ac, self.ac_with_shield = base_ac, ac_with_shield

    def level_up(self):
        self.level += 1
        roll = random.randint(1, self.hit_die)
        self.hp_rolls.append(roll)
        self.proficiency_bonus = 2 + ((self.level - 1) // 4)
        self.recalculate_hp()

    def to_dict(self):
        return {
            "level": self.level,
            "hit_die": self.hit_die,
            "speed": self.speed,
            "proficiency_bonus": self.proficiency_bonus,
            "hp_rolls": self.hp_rolls,
            "char_class": self.char_class,
            "hp_current": self.hp_current,
            "hp_max": self.hp_max,
        }

    @classmethod
    def from_dict(cls, data, abilities):
        return cls(
            level=data["level"],
            hit_die=data["hit_die"],
            abilities=abilities,
            speed=data["speed"],
            proficiency_bonus=data["proficiency_bonus"],
            hp_rolls=data.get("hp_rolls", []),
            char_class=data.get("char_class"),
            hp_current=data.get("hp_current"),
        )
