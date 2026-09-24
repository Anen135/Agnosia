import curses

from display import draw_map_panel
from terminal import show_message


def _available(screen, player, item):
    if player.inventory.get(item, 0) > 0:
        return True
    show_message(screen, f"{item.upper()}: 0")
    screen.getch()
    return False


def use_map(stdscr, player, maze, config):
    if not _available(stdscr, player, "maps"):
        return
    scroll_start = [0, 0]
    charged = False
    while True:
        panel, (max_y, max_x) = draw_map_panel(
            stdscr, maze.maze, player.position, config, scroll_start)
        if not charged:
            player.inventory["maps"] -= 1
            charged = True
        scroll_start[:] = [min(scroll_start[0], max_y), min(scroll_start[1], max_x)]
        key = panel.getch()
        if key == curses.KEY_UP:
            scroll_start[0] = max(0, scroll_start[0] - 1)
        elif key == curses.KEY_DOWN:
            scroll_start[0] = min(max_y, scroll_start[0] + 1)
        elif key == curses.KEY_LEFT:
            scroll_start[1] = max(0, scroll_start[1] - 1)
        elif key == curses.KEY_RIGHT:
            scroll_start[1] = min(max_x, scroll_start[1] + 1)
        elif key in (ord("q"), 27):
            break
    stdscr.clear()
    stdscr.refresh()


def _use_message(screen, player, item, message):
    if not _available(screen, player, item):
        return
    show_message(screen, message)
    player.inventory[item] -= 1
    screen.getch()


def use_compass(stdscr, player, config=None):
    directions = {(1, 0): "South", (0, 1): "East", (-1, 0): "North", (0, -1): "West"}
    _use_message(stdscr, player, "compasses",
                 "Compass: " + directions.get(tuple(player.direction), "Unknown"))


def use_scanner(stdscr, player):
    around = player.look_around()
    cells = " ".join(f"{around[i]},{around[i + 1]}" for i in range(0, len(around), 2))
    _use_message(stdscr, player, "scanners", f"Scanner: [{cells}]")


def use_locator(stdscr, player):
    _use_message(stdscr, player, "locators", f"Locator: [{player.position[0]},{player.position[1]}]")


INVENTORY_ACTIONS = {
    "maps": use_map,
    "compasses": use_compass,
    "scanners": use_scanner,
    "locators": use_locator,
}
