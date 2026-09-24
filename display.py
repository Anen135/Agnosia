import curses
from config import BASEDIR
from terminal import write


def draw_title(stdscr: curses.window):
    """Draw the game title banner."""
    title = (
        "    :::      ::::::::  ::::    :::  ::::::::   :::::::: :::::::::::     :::    \n"
        "  :+: :+:   :+:    :+: :+:+:   :+: :+:    :+: :+:    :+:    :+:       :+: :+:   \n"
        " +:+   +:+  +:+        :+:+:+  +:+ +:+    +:+ +:+           +:+      +:+   +:+  \n"
        "+#++:++#++: :#:        +#+ +:+ +#+ +#+    +:+ +#++:++#++    +#+     +#++:++#++: \n"
        "+#+     +#+ +#+   +#+# +#+  +#+#+# +#+    +#+        +#+    +#+     +#+     +#+ \n"
        "+#+     #+# #+#    #+# #+#   #+#+# #+#    #+# #+#    #+#    #+#     #+#     #+# \n"
        "###     ###  ########  ###    ####  ########   ######## ########### ###     ### "
    )
    for y, line in enumerate(title.splitlines()):
        write(stdscr, y, 0, line)


def draw_game_map(
    stdscr: curses.window,
    layer,
    look_sides,
    message,
    config,
    player,
    timelimit,
):
    """Render the in-game viewport."""
    stdscr.clear()

    # Build content: visible cells around player
    content_lines = []
    for i in range(0, len(look_sides), 2):
        row_idx = look_sides[i]
        col_idx = look_sides[i + 1]
        cell = layer[row_idx][col_idx]
        content_lines.append(f"[{cell}]")
    content = "  ".join(content_lines)

    if message:
        content += "\n" + message

    h, w = stdscr.getmaxyx()
    menu_w = max(1, min(w, max(len(content), 30)))
    menu_h = max(1, min(h, 5))
    menu_x = max(0, (w - menu_w) // 2)
    menu_y = max(0, (h - menu_h) // 2)

    win = curses.newwin(menu_h, menu_w, menu_y, menu_x)
    win.clear()
    for y, line in enumerate(content.splitlines()):
        write(win, y, 0, line)
    win.refresh()

    if timelimit != 0:
        info_x = w - 50
        if info_x > 0 and h >= 23:
            panel = curses.newwin(23, 50, 0, info_x)
            panel.box()
            panel.refresh()


def draw_map_panel(stdscr: curses.window, maze, player_pos, config, scroll_start):
    """Draw a clipped viewport without mutating the maze or its NumPy views."""
    h, w = stdscr.getmaxyx()
    stdscr.keypad(True)
    stdscr.nodelay(False)
    scroll_h = max(1, h - 2)
    scroll_w = max(1, w - 1)
    max_y = max(0, len(maze) - scroll_h)
    max_x = max(0, len(maze[0]) - scroll_w)
    sy = max(0, min(scroll_start[0], max_y))
    sx = max(0, min(scroll_start[1], max_x))
    stdscr.clear()
    for y in range(sy, min(len(maze), sy + scroll_h)):
        row = []
        for x in range(sx, min(len(maze[y]), sx + scroll_w)):
            row.append(str(maze[y][x]))
        write(stdscr, y - sy + 1, 0, "".join(row))
    stdscr.refresh()
    return stdscr, (max_y, max_x)


def draw_live_map(window, maze, player_pos, monster_pos=None):
    """Read-only sidebar viewport that follows the player."""
    height, width = window.getmaxyx()
    window.clear()
    rows, cols = max(1, height - 1), max(1, width - 1)
    sy = max(0, min(player_pos[0] - rows // 2, len(maze) - rows))
    sx = max(0, min(player_pos[1] - cols // 2, len(maze[0]) - cols))
    for y in range(sy, min(len(maze), sy + rows)):
        text = "".join(
            "@" if (y, x) == tuple(player_pos)
            else "M" if monster_pos is not None and (y, x) == tuple(monster_pos)
            else str(maze[y][x])
            for x in range(sx, min(len(maze[y]), sx + cols))
        )
        write(window, y - sy + (1 if height > 1 else 0), 0, text)
    window.refresh()
