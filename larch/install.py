import os
import platform
import shutil
import sys
from pathlib import Path
from typing import List

from colorama import Fore
from RestrictedPython import compile_restricted, safe_globals
from sqlalchemy import delete, insert

from larch import LARCH_PROG_DIR, LARCH_REPO, LARCH_TEMP, passed_to_seed
from larch.cli import progress_fetch
from larch.database.local import LocalPackage, get_installed_pkg_by_name
from larch.database.local import local_db_conn as loccon
from larch.database.local import package_installed
from larch.database.remote import get_remote_candidate, remote_package_exists
from larch.passed_to_seed import copyfile, copytree, join_path, unzip
from larch.utils import set_print_indentaion_lvl
from larch.utils import sp_print as print


def install_seed(seed: str, is_forced=False):
    set_print_indentaion_lvl(0)

    if is_forced:
        print(Fore.YELLOW + f"Forcefully installing '{seed}'...")
    else:
        print(Fore.GREEN + f"Installing '{seed}'...")

    set_print_indentaion_lvl(1)

    seed_code = ""

    with open(seed, mode="r", encoding="utf8") as seed_file:
        seed_code = seed_file.read()

    loc = {}
    byte_code = compile_restricted(seed_code, "<inline>", "exec")
    exec(
        byte_code,
        {
            **safe_globals,
            "join_path": join_path,
            "unzip": unzip,
            "copytree": copytree,
            "copyfile": copyfile,
        },
        loc,
    )

    if package_installed(loc["NAME"]) and not is_forced:
        print(Fore.RED + "Program '{}' already exists, stopping".format(loc["NAME"]))
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

    for dest_file_name, download_url in loc["SOURCE"].items():
        progress_fetch(download_url, temp_dir / dest_file_name)

    passed_to_seed.restricted_dirs = [temp_dir, dest_dir]
    executable_path = loc["install"](temp_dir, dest_dir)  # Execute install func

    loccon.execute(delete(LocalPackage).where(LocalPackage.c.name == loc["NAME"]))
    loccon.execute(
        insert(LocalPackage).values(
            name=loc["NAME"],
            version=".".join((str(i) for i in loc["VERSION"])),
            description=loc["DESCRIPTION"],
            author=loc["AUTHOR"],
            maintainer=loc["MAINTAINER"],
            url=loc["URL"],
            license=loc["LICENSE"],
            executable=executable_path,
        )
    )
    loccon.commit()

    print(
        Fore.GREEN
        + f"'{seed}' was installed successfully! The executable file is '{executable_path}'"
    )
    print("Removing temporary files...")
    shutil.rmtree(temp_dir)

    set_print_indentaion_lvl(0)


def install_seeds(seeds: List[str], is_forced=False):
    set_print_indentaion_lvl(0)

    if is_forced:
        print(Fore.YELLOW + "Installing the following seeds: " + "; ".join(seeds))
    else:
        print("Installing the following seeds: " + Fore.GREEN + "; ".join(seeds))

    for seed in seeds:
        install_seed(seed, is_forced)


def install_pkg_name(pkg_name: str, is_forced=False):
    set_print_indentaion_lvl(0)

    if is_forced:
        print(Fore.YELLOW + f"Forcefully installing '{pkg_name}'...")
    else:
        print(Fore.GREEN + f"Installing '{pkg_name}'...")

    set_print_indentaion_lvl(1)

    package = get_installed_pkg_by_name(pkg_name)

    if package is not None and not is_forced:
        print(
            Fore.RED
            + f"Package '{pkg_name}' is already installed. Did you mean 'larch.py update'?"
        )
        sys.exit(1)

    if not remote_package_exists(pkg_name):
        print(Fore.RED + f"Remote package with name '{pkg_name}' does not exist")
        sys.exit(1)

    remote_pkg = get_remote_candidate(pkg_name)

    if remote_pkg is None:
        print(
            Fore.RED + f"No candidate for package {pkg_name} was found for your system."
        )
        sys.exit(1)

    print("Fetching larchseed.py...", end=" ")
    progress_fetch(
        LARCH_REPO
        + f"packages/{remote_pkg.name}/{remote_pkg.ver}/{remote_pkg.arch}/larchseed.py",
        LARCH_TEMP / "larchseed.py",
    )

    install_seed(LARCH_TEMP / "larchseed.py")
    os.remove(LARCH_TEMP / "larchseed.py")


def install_pkg_names(pkg_names: List[str], is_forced=False):
    set_print_indentaion_lvl(0)

    if is_forced:
        print(
            Fore.YELLOW + "Installing the following packages: " + "; ".join(pkg_names)
        )
    else:
        print("Installing the following packages: " + Fore.GREEN + "; ".join(pkg_names))

    for pkg_name in pkg_names:
        install_pkg_name(pkg_name, is_forced)
