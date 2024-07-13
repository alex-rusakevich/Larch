import subprocess
import sys
from pathlib import Path

from colorama import Fore
from sqlalchemy import select

from larch import LARCH_PROG_DIR
from larch.models import Program, local_db_engine


def run_by_name(is_detached, name, args_list):
    with local_db_engine.connect() as connection:
        prog = connection.execute(
            select(Program).where(Program.c.name == name)
        ).one_or_none()

    if prog is None:
        print(Fore.RED + f"Program '{name}' does not exist, stopping")
        sys.exit(1)

    executable_path = Path(LARCH_PROG_DIR / name) / prog.executable

    if is_detached:
        subprocess.Popen([executable_path, *args_list])
    else:
        subprocess.run([executable_path, *args_list])
