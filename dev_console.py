"""In-game command console; commands operate only on the current player."""
import curses
from collections import deque

from config import INVENTORY_ITEMS
from terminal import write

CONSOLE_KEYS = (ord('`'), ord('~'), curses.KEY_F12)


def execute_command(command, player, settings=None):
    parts = command.lower().split()
    if not parts:
        return ""
    if parts == ["help"]:
        return "mapmode [on|off] | give <item|all> [count] | Items: " + ", ".join(INVENTORY_ITEMS)
    if parts[0] == "mapmode":
        if len(parts) > 2 or (len(parts) == 2 and parts[1] not in ("on", "off")):
            return "Usage: mapmode [on|off]"
        if settings is None:
            return "Map mode settings unavailable."
        settings.map_mode = (not settings.map_mode) if len(parts) == 1 else parts[1] == "on"
        return "Map mode " + ("ON" if settings.map_mode else "OFF")
    if parts[0] != "give":
        return "Unknown command. Type help."
    if len(parts) not in (2, 3):
        return "Usage: give <item|all> [count]"
    item = parts[1]
    if item not in INVENTORY_ITEMS and item != "all":
        return "Unknown item. Use: " + ", ".join(INVENTORY_ITEMS) + ", all"
    try:
        count = int(parts[2]) if len(parts) == 3 else 1
    except ValueError:
        return "Count must be an integer from 1 to 10000."
    if not 1 <= count <= 10000:
        return "Count must be an integer from 1 to 10000."
    if player is None:
        return "Start a level before giving items."
    items = INVENTORY_ITEMS if item == "all" else [item]
    for name in items:
        player.inventory[name] = player.inventory.get(name, 0) + count
    return f"Added {count} to {item}."


class DeveloperConsole:
    def __init__(self):
        self.map_mode = False
        self.output = deque(["Type help for commands."], maxlen=100)

    def open(self, screen, player=None):
        command = ""
        screen.keypad(True)
        while True:
            screen.clear()
            height, width = screen.getmaxyx()
            write(screen, 0, 0, "Developer console | Esc / ~ / F12: close")
            # Wrap output so command help remains readable in narrow terminals.
            lines = []
            columns = max(1, width - 1)
            for message in self.output:
                lines.extend(message[i:i + columns] for i in range(0, len(message), columns))
            available = max(0, height - 2)
            for y, line in enumerate(lines[-available:] if available else [], 1):
                write(screen, y, 0, line)
            prompt = "> " + command + "_"
            write(screen, height - 1, 0, prompt[-columns:])
            screen.refresh()
            key = screen.getch()
            if key in (27, *CONSOLE_KEYS):
                break
            if key in (10, 13, curses.KEY_ENTER):
                if command.strip():
                    self.output.append("> " + command)
                    self.output.append(execute_command(command, player, self))
                command = ""
            elif key in (8, 127, curses.KEY_BACKSPACE):
                command = command[:-1]
            elif 32 <= key <= 126 and len(command) < 256:
                command += chr(key)
        screen.clear()
        screen.refresh()
