import shutil
import sys
from typing import List

from colorama import Fore

from larch import LARCH_PROG_DIR
from larch.installed_db import db_program_exists, db_remove_program
from larch.utils import set_print_indentaion_lvl
from larch.utils import sp_print as print


def uninstall_pkg_name(pkg_name: str):
    print(Fore.GREEN + f"Uninstalling '{pkg_name}'...")

    set_print_indentaion_lvl(1)

    if not db_program_exists(pkg_name):
        print(Fore.RED + "Program '{}' does not exist, stopping".format(pkg_name))
        sys.exit(1)

    db_remove_program(pkg_name)
    shutil.rmtree(LARCH_PROG_DIR / pkg_name)

    print(Fore.GREEN + "Uninstalled '{}' successfully".format(pkg_name))

    set_print_indentaion_lvl(0)


def uninstall_pkg_names(pkg_names: List[str]):
    print("Uninstalling the following packages: " + Fore.GREEN + "; ".join(pkg_names))

    for pkg_name in pkg_names:
        uninstall_pkg_name(pkg_name)
