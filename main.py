"""Agnosia — curses maze escape game.

Entry point. Run with:

    python -m main

or install the package and run:

    agnosia
"""
from game import main
import curses

if __name__ == "__main__":
    curses.wrapper(main)
