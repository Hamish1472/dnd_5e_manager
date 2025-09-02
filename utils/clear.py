import os


def clear_screen():
    """Clear the terminal window."""
    os.system("cls" if os.name == "nt" else "clear")
