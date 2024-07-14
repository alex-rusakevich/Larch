import shutil
import sys
from pathlib import Path
from typing import List

from colorama import Fore
from sqlalchemy import delete

from larch import LARCH_PROG_DIR, LARCH_TEMP, passed_to_seed
from larch.cli import progress_fetch
from larch.database.local import LocalPackage
from larch.database.local import local_db_conn as loccon
from larch.database.local import package_installed
from larch.safe_exec import safe_exec_seed
from larch.utils import set_print_indentaion_lvl
from larch.utils import sp_print as print


def uninstall_pkg_name(pkg_name: str):
    set_print_indentaion_lvl(0)

    print(Fore.GREEN + f"Uninstalling '{pkg_name}'...")

    set_print_indentaion_lvl(1)

    if not package_installed(pkg_name):
        print(Fore.RED + "Package '{}' does not exist, stopping".format(pkg_name))
        sys.exit(1)

    # region Execute uninstall procedure
    loc = safe_exec_seed(Path(LARCH_PROG_DIR / pkg_name, "larchseed.py").read_text())

    temp_dir = Path(LARCH_TEMP / pkg_name)
    dest_dir = Path(LARCH_PROG_DIR / pkg_name)

    temp_dir.mkdir(parents=True, exist_ok=True)

    if callable(loc.get("uninstall", None)):
        for dest_file_name, download_url in loc.get("SOURCE", {}).items():
            progress_fetch(download_url, temp_dir / dest_file_name)

        passed_to_seed.restricted_dirs = [temp_dir, dest_dir]
        loc["uninstall"](temp_dir, dest_dir)
    # endregion

    # region Unregister package
    loccon.execute(delete(LocalPackage).where(LocalPackage.c.name == pkg_name))
    loccon.commit()
    # endregion

    # region Cleaning
    shutil.rmtree(temp_dir)
    shutil.rmtree(dest_dir)
    # endregion

    print(Fore.GREEN + "Uninstalled '{}' successfully".format(pkg_name))

    set_print_indentaion_lvl(0)


def uninstall_pkg_names(pkg_names: List[str]):
    print("Uninstalling the following packages: " + Fore.GREEN + "; ".join(pkg_names))

    for pkg_name in pkg_names:
        uninstall_pkg_name(pkg_name)
