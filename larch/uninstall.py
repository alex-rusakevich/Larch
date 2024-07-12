import shutil
import sys
from typing import List

from larch import LARCH_PROG_DIR
from larch.installed_db import db_program_exists, db_remove_program


def uninstall_pkg_name(pkg_name: str):
    print(f"Uninstalling '{pkg_name}'...")

    if not db_program_exists(pkg_name):
        print("Program '{}' does not exist, stopping".format(pkg_name))
        sys.exit(1)

    db_remove_program(pkg_name)
    shutil.rmtree(LARCH_PROG_DIR / pkg_name)

    print("Uninstalled '{}' successfully".format(pkg_name))


def uninstall_pkg_names(pkg_names: List[str]):
    for pkg_name in pkg_names:
        uninstall_pkg_name(pkg_name)
