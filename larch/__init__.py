import platform
from pathlib import Path

__version__ = "0.2.0"

LARCH_DIR = Path().home() / ".larch"
LARCH_TEMP = LARCH_DIR / "temp"
LARCH_PROG_DIR = LARCH_DIR / "packages"
LARCH_CACHE = LARCH_DIR / "cache"

Path.mkdir(LARCH_DIR, parents=True, exist_ok=True)
Path.mkdir(LARCH_TEMP, parents=True, exist_ok=True)
Path.mkdir(LARCH_PROG_DIR, parents=True, exist_ok=True)
Path.mkdir(LARCH_CACHE, parents=True, exist_ok=True)

LARCH_REPO = "https://github.com/alex-rusakevich/larchseed_warehouse/raw/master/"
CURRENT_ARCH = platform.system() + "_" + platform.architecture()[0]
