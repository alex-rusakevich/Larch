import subprocess
import sys
from pathlib import Path

from colorama import Fore

from larch import LARCH_PROG_DIR
from larch.installed_db import db_get_program_by_name


def run_by_name(is_detached, name, args_list):
    prog = db_get_program_by_name(name)

    if prog is None:
        print(Fore.RED + f"Program '{name}' does not exist, stopping")
        sys.exit(1)

    executable_path = Path(LARCH_PROG_DIR / name) / prog["executable_path"]

    if is_detached:
        subprocess.Popen([executable_path, *args_list])
    else:
        subprocess.run([executable_path, *args_list])
