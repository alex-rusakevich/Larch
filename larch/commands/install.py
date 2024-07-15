import os
import platform
import re
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from colorama import Fore
from sqlalchemy import delete, insert

from larch import LARCH_PROG_DIR, LARCH_REPO, LARCH_TEMP
from larch.database.local import LocalPackage, get_installed_pkg_by_name
from larch.database.local import local_db_conn as loccon
from larch.database.local import package_installed
from larch.database.remote import get_remote_candidate, remote_package_exists
from larch.sandbox import passed_funcs
from larch.sandbox.safe_exec import safe_exec_seed
from larch.utils import progress_fetch, set_print_indentation_lvl
from larch.utils import sp_print as print


def install_seed(seed: str, is_forced=False):
    if is_forced:
        print(Fore.YELLOW + f"Forcefully installing '{seed}'...")
    else:
        print(Fore.GREEN + f"Installing '{seed}'...")

    set_print_indentation_lvl(1)

    seed_code = ""

    with open(seed, mode="r", encoding="utf8") as seed_file:
        seed_code = seed_file.read()

    loc = safe_exec_seed(seed_code)

    if package_installed(loc["NAME"]) and not is_forced:
        print(
            Fore.RED
            + "Package '{}' has been installed already, stopping".format(loc["NAME"])
        )
        sys.exit(1)

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

    # region Install dependencies
    deps = loc.get("DEPENDENCIES", None)

    if deps:
        print("Installing dependencies: " + Fore.GREEN + "; ".join(deps) + Fore.RESET)
        install_packages(deps, is_forced=True)
    # endregion

    for dest_file_name, download_url in loc.get("SOURCE", {}).items():
        progress_fetch(download_url, temp_dir / dest_file_name)

    passed_funcs.restricted_dirs = [temp_dir, dest_dir]
    loc["install"](temp_dir, dest_dir)  # Execute install func

    # region Registering package
    shutil.copy(seed, dest_dir)
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


def install_pkg(
    pkg_name: str,
    desired_ver: Optional[Tuple[str, str]] = None,
    is_forced: bool = False,
):
    ver_str = ""

    if desired_ver is not None:
        ver_str = "".join(desired_ver)

    if is_forced:
        print(Fore.YELLOW + f"Forcefully installing '{pkg_name}{ver_str}'...")
    else:
        print(f"Installing '{pkg_name}{ver_str}'...")

    set_print_indentation_lvl(1)

    package = get_installed_pkg_by_name(pkg_name)

    if package is not None and not is_forced:
        print(Fore.RED + f"Package '{pkg_name}' is already installed, stopping")
        sys.exit(1)

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

    install_seed(seed_path, is_forced)
    os.remove(seed_path)


def install_packages(pkg_names: List[str], is_forced=False):
    set_print_indentation_lvl(0)

    for i, val in enumerate(pkg_names):
        pkg_names[i] = re.sub(r"\s*", "", val)

    if is_forced:
        print(
            Fore.YELLOW
            + "Forcefully installing the following packages: "
            + "; ".join(pkg_names)
        )
    else:
        print("Installing the following packages: " + Fore.GREEN + "; ".join(pkg_names))

    for pkg in pkg_names:
        _, file_name = os.path.split(pkg)
        set_print_indentation_lvl(0)

        if file_name == "larchseed.py":
            install_seed(pkg, is_forced)
        else:
            pkg_name = re.sub(r"(>=|==|<=|<|>).*", "", pkg).strip()

            pkg_ver = re.search(r"(>=|==|<=|<|>)(.*)", pkg)
            if pkg_ver:
                pkg_ver = (pkg_ver.group(1), pkg_ver.group(2).strip())

            if type(pkg_ver) in (list, tuple):
                if not pkg_ver[0] or not pkg_ver[1]:
                    print(Fore.RED + f"Wrong version format: '{pkg}', stopping")
                    sys.exit(1)

            install_pkg(pkg_name, pkg_ver, is_forced=is_forced)
