import random


def roll_dice(num=1, sides=6):
    """Roll N dice with given sides and return a list of results."""
    return [random.randint(1, sides) for _ in range(num)]


def roll_ability():
    """Roll 4d6, drop the lowest, return the sum."""
    rolls = roll_dice(4, 6)
    print(f"Dice rolled: {rolls}, dropping lowest {min(rolls)}")
    return sum(sorted(rolls)[1:])
