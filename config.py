from pathlib import Path

BASEDIR = Path(__file__).resolve().parent
LEVELS_DIR = BASEDIR / "levels"
MUSIC_DIR = BASEDIR / "music"

DEFAULT_CONFIG = {
    "wall": "#",
    "path": " ",
    "start": "S",
    "end": "E",
}

INVENTORY_ITEMS = ["maps", "compasses", "scanners", "locators"]
