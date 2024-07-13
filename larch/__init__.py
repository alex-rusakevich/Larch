from pathlib import Path

__version__ = (0, 0, 1)

LARCH_DIR = Path().home() / ".larch"
LARCH_TEMP = LARCH_DIR / "temp"
LARCH_PROG_DIR = LARCH_DIR / "programs"
LARCH_CACHE = LARCH_DIR / "cache"

Path.mkdir(LARCH_DIR, parents=True, exist_ok=True)
Path.mkdir(LARCH_TEMP, parents=True, exist_ok=True)
Path.mkdir(LARCH_PROG_DIR, parents=True, exist_ok=True)
Path.mkdir(LARCH_CACHE, parents=True, exist_ok=True)

LARCH_REPO = "https://github.com/alex-rusakevich/larchseed_warehouse/raw/master/"
