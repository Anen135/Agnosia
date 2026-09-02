import curses
from config import INVENTORY_ITEMS
from entity import Player


def use_map(stdscr: curses.window, player: Player, maze, config):
    if player.inventory["maps"] == 0:
        stdscr.addstr("You don't have any maps!\n")
        stdscr.refresh()
        stdscr.getch()
        return

    player.inventory["maps"] -= 1
    scroll_start = [0, 0]

    while True:
        panel, (max_y, max_x) = draw_map_panel(stdscr, maze.maze, player.position, config, scroll_start)
        stdscr.nodelay(False)

        key = stdscr.getch()
        sy, sx = scroll_start

        if key == curses.KEY_UP and sy > 0:
            scroll_start[0] -= 1
        elif key == curses.KEY_DOWN and sy < max_y:
            scroll_start[0] += 1
        elif key == curses.KEY_LEFT and sx > 0:
            scroll_start[1] -= 1
        elif key == curses.KEY_RIGHT and sx < max_x:
            scroll_start[1] += 1
        elif key == ord("q"):
            break


def use_compass(stdscr: curses.window, player: Player, config):
    if player.inventory["compasses"] == 0:
        stdscr.addstr("You don't have any compasses!\n")
        stdscr.refresh()
        stdscr.getch()
        return

    player.inventory["compasses"] -= 1
    stdscr.addstr("Voice: ")
    stdscr.addstr("There's darkness everywhere\n", curses.color_pair(1))

    direction_names = {
        (1, 0): "0",
        (0, 1): "1",
        (-1, 0): "2",
        (0, -1): "3",
    }
    stdscr.addstr("Compass: ")
    stdscr.addstr(direction_names.get(tuple(player.direction), "?"), curses.color_pair(1))
    stdscr.addstr("\n")
    stdscr.refresh()
    stdscr.getch()


def use_scanner(stdscr: curses.window, player: Player):
    if player.inventory["scanners"] == 0:
        stdscr.addstr("You don't have any scanners!\n")
        stdscr.refresh()
        stdscr.getch()
        return

    player.inventory["scanners"] -= 1
    stdscr.addstr("Voice: ")
    stdscr.addstr("These walls are familiar to you?\n", curses.color_pair(1))
    stdscr.addstr("Scanner: [")
    around = player.look_around()
    for i in range(0, len(around), 2):
        stdscr.addstr(f"{around[i]},{around[i+1]} ")
    stdscr.addstr("]\n")
    stdscr.refresh()
    stdscr.getch()


def use_locator(stdscr: curses.window, player: Player):
    if player.inventory["locators"] == 0:
        stdscr.addstr("You don't have any locators!\n")
        stdscr.refresh()
        stdscr.getch()
        return

    player.inventory["locators"] -= 1
    stdscr.addstr("Voice: ")
    stdscr.addstr("I can see you...\n", curses.color_pair(1))
    stdscr.addstr("Locator: ")
    stdscr.addstr(f"[{player.position[0]},{player.position[1]}]\n\n")
    stdscr.refresh()
    stdscr.getch()


INVENTORY_ACTIONS = {
    "maps": use_map,
    "compasses": use_compass,
    "scanners": use_scanner,
    "locators": use_locator,
}
