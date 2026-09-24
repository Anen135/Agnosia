"""Agnosia — curses maze escape game.

Entry point. Run with:

    python -m main

or install the package and run:

    agnosia
"""
from game import main as run_game
import curses
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path


def main():
    log_path = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Agnosia" / "agnosia.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=2, encoding="utf-8")
    except OSError:
        handler = logging.StreamHandler()
    logging.basicConfig(level=logging.WARNING, handlers=[handler],
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s", force=True)
    try:
        curses.wrapper(run_game)
    except KeyboardInterrupt:
        return 0
    except Exception:
        logging.exception("Game terminated unexpectedly")
        print(f"The game could not continue. Error details: {getattr(handler, 'baseFilename', 'stderr')}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
