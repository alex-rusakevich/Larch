from larch.installed_db import db_get_program_by_name
from larch import LARCH_PROG_DIR
import sys
import subprocess
from pathlib import Path


def run_by_name(name, args_list):
    prog = db_get_program_by_name(name)

    if prog is None:
        print(f"Program '{name}' does not exist, stopping")
        sys.exit(1)

    executable_path = Path(LARCH_PROG_DIR / name) / prog["executable_path"]
    subprocess.run([executable_path, *args_list])
