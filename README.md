# Agnosia

Terminal maze game. Python 3.10 or newer.

On Windows, install dependencies and run from the project directory:

```powershell
python -m pip install numpy windows-curses
python -m main
```

Use an interactive terminal, such as PowerShell or Windows Terminal.
Choose menu items with the arrow keys or numbers, then press Enter.
Press `q` or Escape to go back (or quit from the main menu).
In the map, use arrow keys to scroll and `q` or Escape to return.
Each map opening consumes one map; scrolling does not consume more.
The map item shows only the maze structure, without a player marker.
Small terminals show fewer menu entries, keeping the selection visible.

Open the developer console from any menu with the backtick/tilde key or F12.
Close it with the same key or Escape. Start a level before issuing items;
items belong to the current run. Commands (press Enter to execute):

```text
help
mapmode on
mapmode off
give maps 5
give compasses 2
give scanners 3
give locators
give all 10
```

The default count is 1; accepted counts are integers from 1 to 10000.

`mapmode on` keeps a live map on the right during gameplay and in the inventory
menu, with `@` marking the player. Large maps scroll to follow the player.
It does not consume map items. `mapmode off` hides it; `mapmode` toggles it.
This setting lasts until changed or the application exits. The console and
item views temporarily replace the gameplay view. In terminals narrower than
8 columns the sidebar is hidden until the window is enlarged.

The tutorial has no monster. The following level contains a random wanderer
(`M` in the developer map). It takes one step after GO, BACK, LEFT or RIGHT,
including a blocked GO. It has no perception or pursuit logic. Menus and
inventory do not advance it. Sharing a cell ends the run; starting again
spawns a new monster. Escaping selects the next level for the next START.
The map item shows neither entity. In-game maps have no legend or controls
overlay; controls are documented here rather than explained during play.

Invalid level files are skipped. If no valid levels remain, the game uses
a built-in level. Maze dimensions must be odd integers from 3 through 501.
Missing audio does not stop gameplay. Audio playback is Windows-only.

Warnings and unexpected errors are logged to
`%LOCALAPPDATA%\Agnosia\agnosia.log` on Windows, or
`~/Agnosia/agnosia.log` otherwise. Logs rotate automatically.

Run regression tests:

```powershell
python -m unittest discover
```
