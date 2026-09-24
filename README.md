<div align="center">

# A G N O S I A

**A labyrinth. A terminal. No guide.**

`PYTHON 3.10+` · `CURSES` · `ASCII` · `IN DEVELOPMENT`

```text
#############################
#       #           #       #
# ##### # ######### # ##### #
# #   #   #       #   #     #
# # ##### # ##### ##### ### #
#   #     #     #       #   #
#############################
```

*You are given a world. The rest is yours to discover.*

</div>

---

## Beyond the prompt

**Agnosia** is a turn-based maze escape game that lives in your terminal. There are walls, passages, a handful of items, and commands. From these fragments, you must piece together a sense of the place you have entered.

Its aesthetic draws on the terminal games of the 1970s: sparse, hostile, idiosyncratic, yet full of soul. A black screen, text, ASCII, and the silence between decisions. The interface makes no effort to charm you. The world does not pause to explain itself.

There is no hand-holding. You are given a space and the freedom to explore it: test a hunch, remember a turn, make a mistake, find your way back. A map does not have to answer “where am I?” An item does not have to reveal everything you want to know. Understanding comes through experience.

**Stability is a requirement for the code. Obscurity is part of the design.** A software error should never cut an exploration short; the absence of a hint may be where one begins.

## What lives in the labyrinth

- Generated mazes and levels defined in JSON.
- Movement relative to your facing direction: forward, turn around, left, right.
- A limited supply of maps, compasses, scanners, and locators.
- A map with no marker for your position: only the shape of the space.
- A tutorial level, followed by a labyrinth where you are no longer alone.

Something wanders there. It is deaf and blind. It does not know where you are. Sometimes that is enough.

The project is in development: mechanics and balance are still changing. Its distinct character, restraint, and exploration without a guide remain at its core.

> This page describes the current working version. Inventory updates, the developer console, and the monster are still in local development and have not yet been published to `main` on GitHub.

## Enter

You need **Python 3.10+** and an interactive terminal. On Windows, PowerShell and Windows Terminal will do.

```powershell
git clone https://github.com/Anen135/Agnosia.git
cd Agnosia
python -m venv venv
.\venv\Scripts\python.exe -m pip install numpy windows-curses
.\venv\Scripts\python.exe -m main
```

<details>
<summary>Linux / macOS</summary>

Your Python installation must include `curses` support. Audio playback is available on Windows only.

```sh
git clone https://github.com/Anen135/Agnosia.git
cd Agnosia
python3 -m venv venv
./venv/bin/python -m pip install numpy
./venv/bin/python -m main
```

</details>

<details>
<summary>Controls</summary>

| Where | Action | Keys |
| --- | --- | --- |
| Menus | Select an option | ↑ / ↓ or the option number |
| Menus | Confirm | Enter or Space |
| Menus | Go back; quit from the main menu | Esc or `q` |
| Map | Scroll | Arrow keys |
| Map | Close | Esc or `q` |

`BACK` in the movement menu means turn around. Opening a map consumes one item; scrolling does not consume additional maps.

</details>

## Behind the screen

The details below reveal game mechanics. You do not need them for your first visit.

<details>
<summary>Developer console</summary>

Open it from a menu with the **tilde / backtick key** or **F12**. Close it with the same key or **Esc**. Press Enter to execute a command.

| Command | Action |
| --- | --- |
| `help` | List commands |
| `give maps 5` | Add five maps |
| `give compasses 2` | Add two compasses |
| `give scanners 3` | Add three scanners |
| `give locators` | Add one locator |
| `give all 10` | Add ten of each item |
| `mapmode on` | Show the live map on the right |
| `mapmode off` | Hide the live map |
| `mapmode` | Toggle map mode |

Items can be granted after a level starts and belong to the current run. The count must be an integer from 1 to 10000; the default is 1.

In `mapmode`, `@` marks the player and `M` marks the monster. Large maps scroll to follow the player. This mode consumes no items and stays enabled until switched off or the application exits. The console and item screens temporarily replace the gameplay view. The sidebar is hidden when the terminal is narrower than eight columns.

</details>

<details>
<summary>Levels and monster behavior</summary>

Levels live in [`levels/`](levels/). Maze dimensions must be odd integers from 3 to 501. The JSON field `monster` accepts `null` or `"wanderer"`.

The tutorial has no monster. In the next level, it spawns in a random passage, away from the starting cell and the exit. After `GO`, `BACK`, `LEFT`, or `RIGHT`, it chooses a random adjacent walkable cell. Trying to walk into a wall also gives it a turn. Navigating menus and using the inventory do not.

The monster has no perception, pathfinding toward the player, or pursuit behavior. Sharing a cell ends the run: both the player stepping onto the monster and the monster stepping onto the player are checked. A new run spawns the monster anew. After an escape, the next level is selected for the next `START`.

The ordinary map shows neither the player nor the monster.

</details>

<details>
<summary>Tests and diagnostics</summary>

From the project root, using an environment with the dependencies installed:

```sh
python -m unittest discover
```

Regression tests cover inventory, maps, terminal dimensions, console commands, level loading, movement, and monster collisions.

Invalid levels are skipped. If no valid levels remain, a fallback level is loaded. Unavailable audio does not stop the game. Unexpected errors are written to a rotating log:

- Windows: `%LOCALAPPDATA%\Agnosia\agnosia.log`
- Linux / macOS: `~/Agnosia/agnosia.log`

When reporting a bug, include the steps to reproduce it, your Python version, your terminal, and the relevant log excerpt.

</details>

---

<div align="center">

*The labyrinth never promised you anything.*

</div>
