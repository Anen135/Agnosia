import curses
from config import BASEDIR


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
    stdscr.addstr(title)


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
    menu_w = max(len(content), 30)
    menu_x = max(0, (w - menu_w) // 2)
    menu_y = max(0, (h - 5) // 2)

    win = curses.newwin(5, menu_w, menu_y, menu_x)
    win.clear()
    win.addstr(0, 0, content[:menu_w - 1])
    win.refresh()

    if timelimit != 0:
        info_x = w - 50
        if info_x > 0:
            panel = curses.newwin(23, 50, 0, info_x)
            panel.box()
            panel.refresh()


def draw_map_panel(stdscr: curses.window, maze, player_pos, config, scroll_start):
    """Render the scrollable map overlay for the map item."""
    h, w = stdscr.getmaxyx()
    panel_x = max(0, w - 50)
    panel_y = 0
    panel = curses.newwin(23, 50, panel_y, panel_x)

    scroll_h = 10
    scroll_w = 20
    max_scroll_y = max(0, len(maze) - scroll_h)
    max_scroll_x = max(0, len(maze[0]) - scroll_w)

    sy, sx = scroll_start
    panel.clear()
    buffer = maze[sy:sy + scroll_h, sx:sx + scroll_w]
    buffer[player_pos[0] - sy][player_pos[1] - sx] = "O"

    panel.addstr(0, 0, f"Scroll: {sy} {sx} {max_scroll_y} {max_scroll_x}  (q to exit)")

    for y, row in enumerate(buffer):
        for x, cell in enumerate(row):
            if cell in (config["start"], config["end"]):
                panel.addch(y + 1, x + 2, cell, curses.color_pair(1))
            else:
                panel.addch(y + 1, x + 2, cell)

    panel.refresh()
    return panel, (max_scroll_y, max_scroll_x)
