from InquirerPy import inquirer
from data.weapons import WEAPONS
from data.class_equipment import CLASS_STARTING_EQUIPMENT


def select_starting_equipment(char_class):
    """
    Generate starting equipment for a given class.
    Handles:
    - Static items
    - a/b bundles
    - Generic selections like "any simple weapon" or "any martial melee weapon"
    - Displays duplicates as (xN) in selection menus
    - Accurately adds the correct quantity to final equipment
    """
    final_equipment = []

    for block in CLASS_STARTING_EQUIPMENT.get(char_class, []):
        # Add static items automatically
        if "static" in block:
            final_equipment.extend(block["static"])

        # Handle choices (a/b)
        elif "choice" in block:
            # Prepare display options for user
            display_options = []
            for option in block["choice"]:
                if isinstance(option, list):
                    # Count duplicates in the bundle
                    counts = {}
                    for i in option:
                        counts[i] = counts.get(i, 0) + 1
                    # Format duplicates as "Handaxe (x2)" for display
                    display_options.append(
                        " + ".join(
                            f"{i} (x{c})" if c > 1 else i for i, c in counts.items()
                        )
                    )
                else:
                    display_options.append(option)

            # Ask user to pick a/b
            selected_option = inquirer.select(
                message="Choose an option:", choices=display_options
            ).execute()

            # Split bundles back into individual items with correct quantity
            items = []
            for part in selected_option.split(" + "):
                if " (x" in part:
                    item_name, qty_str = part.split(" (x")
                    qty = int(qty_str.rstrip(")"))
                    items.extend([item_name] * qty)
                else:
                    items.append(part)

            # Resolve any generic weapon selections inside items
            resolved_items = []

            for item in items:
                item_lower = item.lower()

                # Determine weapon type
                weapon_type = None
                if "simple" in item_lower:
                    weapon_type = "simple"
                elif "martial" in item_lower:
                    weapon_type = "martial"

                # Determine weapon category
                weapon_category = None
                if "melee" in item_lower:
                    weapon_category = "melee"
                elif "ranged" in item_lower:
                    weapon_category = "ranged"

                # If it's a weapon choice
                if weapon_type or weapon_category:
                    valid_weapons = [
                        w
                        for w, attr in WEAPONS.items()
                        if (
                            weapon_type is None
                            or (
                                attr["simple"]
                                if weapon_type == "simple"
                                else not attr["simple"]
                            )
                        )
                        and (
                            weapon_category is None
                            or (
                                attr["ranged"]
                                if weapon_category == "ranged"
                                else not attr["ranged"]
                            )
                        )
                    ]
                    choice = inquirer.select(
                        message=f"Choose {item}:", choices=valid_weapons
                    ).execute()
                    resolved_items.append(choice)
                else:
                    resolved_items.append(item)

            # Add all resolved items to final equipment
            final_equipment.extend(resolved_items)

    return final_equipment
