import os
import platform
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from colorama import Fore
from sqlalchemy import delete, insert

from larch import LARCH_PROG_DIR, LARCH_REPO, LARCH_TEMP
from larch.database.local import LocalPackage
from larch.database.local import local_db_conn as loccon
from larch.database.remote import get_remote_candidate, remote_package_exists
from larch.dep_tree.node import Node
from larch.sandbox import passed_funcs
from larch.sandbox.safe_exec import safe_exec_seed
from larch.utils import progress_fetch, set_print_indentation_lvl
from larch.utils import sp_print as print


def install_seed(seed_code: str) -> str:
    set_print_indentation_lvl(0)

    loc = safe_exec_seed(seed_code)

    ver = loc["VERSION"]

    if type(ver) is not str:
        ver = ".".join(str(i) for i in ver)

    print(Fore.GREEN + "Installing " + loc["NAME"] + "==" + ver + "...")

    # region Preparing directories
    temp_dir = Path(LARCH_TEMP / loc["NAME"])
    dest_dir = Path(LARCH_PROG_DIR / loc["NAME"])

    try:
        if temp_dir.exists() and temp_dir.is_dir():
            shutil.rmtree(temp_dir)
    except PermissionError:
        print(
            Fore.RED
            + f"Cannot remove folder '{temp_dir}'. \
Make sure that the folder you are trying to delete is not used by a currently running program"
        )
        sys.exit(1)

    try:
        if dest_dir.exists() and dest_dir.is_dir():
            shutil.rmtree(dest_dir)
    except PermissionError:
        print(
            Fore.RED
            + f"Cannot remove folder '{dest_dir}'. \
Make sure that the folder you are trying to delete is not used by a currently running program"
        )
        sys.exit(1)

    Path.mkdir(temp_dir)
    Path.mkdir(dest_dir)
    # endregion

    # region Check arch
    arch = loc.get("ARCH", None)
    current_arch = platform.system() + "_" + platform.architecture()[0]

    if arch is not None:
        if current_arch not in arch:
            print(
                Fore.RED
                + f"The package '{loc['NAME']}' is not supported by your machine"
            )
            print(
                Fore.RED
                + f"Package arch: {', '.join(arch)}, your machine's arch: {current_arch}"
            )
            sys.exit(1)
    # endregion

    print(
        Fore.YELLOW
        + f"By installing '{loc['NAME']}', you accept it's license: {loc['LICENSE']}"
    )

    for dest_file_name, download_url in loc.get("SOURCE", {}).items():
        progress_fetch(download_url, temp_dir / dest_file_name)

    passed_funcs.restricted_dirs = [temp_dir, dest_dir]
    loc["install"](temp_dir, dest_dir)  # Execute install func

    # region Registering package
    open(os.path.join(dest_dir, "larchseed.py"), "w", encoding="utf8").write(seed_code)

    entry_point = loc.get("ENTRY_POINT", None)
    ver = loc["VERSION"]

    if type(ver) in (tuple, list):
        ver = ".".join((str(i) for i in loc["VERSION"]))
    elif type(ver) is str:
        pass
    else:
        print(
            Fore.RED
            + f"Unknown VERSION type: {type(ver)}, allowed types are str, tuple and list"
        )

    loccon.execute(delete(LocalPackage).where(LocalPackage.c.name == loc["NAME"]))
    loccon.execute(
        insert(LocalPackage).values(
            name=loc["NAME"],
            version=ver,
            description=loc["DESCRIPTION"],
            author=loc["AUTHOR"],
            maintainer=loc["MAINTAINER"],
            url=loc["URL"],
            license=loc["LICENSE"],
            entry_point=entry_point,
        )
    )
    loccon.commit()
    # endregion

    print(Fore.GREEN + f"'{loc['NAME']}=={ver}' was installed successfully!")
    entry_point and print(f"The entry point is '{entry_point}'")
    print("Removing temporary files...")
    shutil.rmtree(temp_dir)

    set_print_indentation_lvl(0)


def install_pkg(pkg_name: str, desired_ver: Optional[Tuple[str, str]] = None):
    # region Skipping installed
    pkg_str = pkg_name

    if desired_ver and desired_ver[0] and desired_ver[1]:
        pkg_str += desired_ver[0] + desired_ver[1]

    for node in Node.all_nodes:
        if node.pkg_str == pkg_str:
            if node.node_type == Node.NodeType.INSTALLED:
                return

            break
    # endregion

    ver_str = ""

    if desired_ver is not None:
        ver_str = "".join(desired_ver)

    print(f"Installing '{pkg_name}{ver_str}'...")

    set_print_indentation_lvl(1)

    if not remote_package_exists(pkg_name):
        print(Fore.RED + f"Remote package with name '{pkg_name}' does not exist")
        sys.exit(1)

    remote_pkg = get_remote_candidate(pkg_name, desired_ver)

    if remote_pkg is None:
        print(
            Fore.RED
            + f"No candidate for package '{pkg_name}{ver_str}' was found for your system."
        )
        sys.exit(1)
    else:
        print(Fore.GREEN + f"Found package: {remote_pkg.name}=={remote_pkg.ver}")

    seed_path = os.path.join(
        LARCH_TEMP,
        ".seeds",
        remote_pkg.name,
        remote_pkg.ver,
        remote_pkg.arch,
        "larchseed.py",
    )
    Path(os.path.dirname(seed_path)).mkdir(parents=True, exist_ok=True)

    progress_fetch(
        LARCH_REPO
        + f"packages/{remote_pkg.name}/{remote_pkg.ver}/{remote_pkg.arch}/larchseed.py",
        seed_path,
    )

    install_seed(Path(seed_path).read_text())
    os.remove(seed_path)


def _install_packages():
    set_print_indentation_lvl(0)

    current_queue = []
    next_queue = []

    for node in Node.all_nodes:
        if node.children == []:
            current_queue.append(node)

    while len(current_queue) > 0:
        for node in current_queue:
            if node.name in ("@user", "@local"):
                continue

            if node.node_type == Node.NodeType.REMOTE:
                install_seed(node.seed_code)

            next_queue = [*next_queue, *node.parents]

        current_queue = next_queue
        next_queue = []


def install_packages(pkg_names: List[str]):
    set_print_indentation_lvl(0)

    user_root = Node([], list(Node([], [], pkg_str) for pkg_str in pkg_names), "@user")
    Node.shake_tree()

    # pprint(Node.all_nodes)

    skipped = []
    installing = []

    for child in user_root.children:
        if child.node_type == Node.NodeType.INSTALLED:
            skipped.append(child.pkg_str)
        else:
            installing.append(child.pkg_str)

    skipped and print(
        Fore.YELLOW
        + "The following package(s) were installed already: "
        + "; ".join(skipped)
    )

    if len(installing) == 0:
        print(Fore.RED + "Nothing to install, stopping")
    else:
        print(
            "Installing the following package(s): " + Fore.GREEN + "; ".join(installing)
        )
        _install_packages()
