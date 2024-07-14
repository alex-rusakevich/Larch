import shutil
import sys
from typing import List

from colorama import Fore
from sqlalchemy import delete

from larch import LARCH_PROG_DIR
from larch.database.local import LocalPackage
from larch.database.local import local_db_conn as loccon
from larch.database.local import package_installed
from larch.utils import set_print_indentaion_lvl
from larch.utils import sp_print as print


def uninstall_pkg_name(pkg_name: str):
    set_print_indentaion_lvl(0)

    print(Fore.GREEN + f"Uninstalling '{pkg_name}'...")

    set_print_indentaion_lvl(1)

    if not package_installed(pkg_name):
        print(Fore.RED + "Package '{}' does not exist, stopping".format(pkg_name))
        sys.exit(1)

    loccon.execute(delete(LocalPackage).where(LocalPackage.c.name == pkg_name))
    loccon.commit()
    shutil.rmtree(LARCH_PROG_DIR / pkg_name)

    print(Fore.GREEN + "Uninstalled '{}' successfully".format(pkg_name))

    set_print_indentaion_lvl(0)


def uninstall_pkg_names(pkg_names: List[str]):
    print("Uninstalling the following packages: " + Fore.GREEN + "; ".join(pkg_names))

    for pkg_name in pkg_names:
        uninstall_pkg_name(pkg_name)
