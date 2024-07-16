import shutil
import sys
from pathlib import Path
from typing import List

from colorama import Fore
from sqlalchemy import delete

from larch import LARCH_PROG_DIR, LARCH_TEMP
from larch.database.local import LocalPackage
from larch.database.local import local_db_conn as loccon
from larch.database.local import package_installed
from larch.dep_tree.node import Node
from larch.sandbox import passed_funcs
from larch.sandbox.safe_exec import safe_exec_seed
from larch.utils import progress_fetch, set_print_indentation_lvl
from larch.utils import sp_print as print


def uninstall_pkg_name(pkg_name: str):
    set_print_indentation_lvl(0)

    print(Fore.GREEN + f"Uninstalling '{pkg_name}'...")

    set_print_indentation_lvl(1)

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

        passed_funcs.restricted_dirs = [temp_dir, dest_dir]
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

    set_print_indentation_lvl(0)


def uninstall_pkg_names(pkg_names: List[str]):
    set_print_indentation_lvl(0)

    Node([], list(Node([], [], pkg_str) for pkg_str in pkg_names), "@user")

    Node.shake_tree()

    for pkg_name in pkg_names:
        broken_parent_pkg = []

        for node in Node.all_nodes:
            if node.name == pkg_name:  # Found corresponding node in the tree
                for node_parent in node.parents:
                    if node_parent.name not in ("@user", "@local", *pkg_names):
                        broken_parent_pkg.append(node_parent)
                break

        if broken_parent_pkg:
            broken_parent_pkg_names = "; ".join(set(i.name for i in broken_parent_pkg))
            print(
                Fore.RED
                + f"Cannot uninstall '{pkg_name}' because it will break the following packages: {broken_parent_pkg_names}"
            )
            sys.exit(1)

    print("Uninstalling the following package(s): " + Fore.GREEN + "; ".join(pkg_names))

    for pkg_name in pkg_names:
        uninstall_pkg_name(pkg_name)
