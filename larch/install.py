import shutil
import sys
from pathlib import Path
from typing import List
from colorama import Fore

from RestrictedPython import compile_restricted, safe_globals

from larch import LARCH_PROG_DIR, LARCH_TEMP
from larch.cli import progress_fetch
from larch.installed_db import db_add_new_program, db_program_exists, db_update_program
from larch.passed_to_seed import copy, join_path, unzip


def install_seed(seed: str, is_forced=False):
    if is_forced:
        print(Fore.YELLOW + f"Forcefully installing '{seed}'...")
    else:
        print(Fore.GREEN + f"Installing '{seed}'...")
    seed_code = ""

    with open(seed, mode="r", encoding="utf8") as seed_file:
        seed_code = seed_file.read()

    loc = {}
    byte_code = compile_restricted(seed_code, "<inline>", "exec")
    exec(
        byte_code,
        {**safe_globals, "join_path": join_path, "unzip": unzip, "copy": copy},
        loc,
    )

    if db_program_exists(loc["NAME"]) and not is_forced:
        print("Program '{}' already exists, stopping".format(loc["NAME"]))
        sys.exit(1)

    # region Preparing directories
    temp_dir = Path(LARCH_TEMP / loc["NAME"])
    dest_dir = Path(LARCH_PROG_DIR / loc["NAME"])

    try:
        if temp_dir.exists() and temp_dir.is_dir():
            shutil.rmtree(temp_dir)

        if dest_dir.exists() and dest_dir.is_dir():
            shutil.rmtree(dest_dir)
    except PermissionError:
        print(
            f"Cannot remove folder '{temp_dir}'. \
Make sure that the folder you are trying to delete is not used by a currently running program"
        )

    Path.mkdir(temp_dir)
    Path.mkdir(dest_dir)
    # endregion

    for dest_file_name, download_url in loc["SOURCE"].items():
        progress_fetch(download_url, temp_dir / dest_file_name)

    executable_path = loc["install"](temp_dir, dest_dir)

    if db_program_exists(loc["NAME"]):
        db_update_program(
            name=loc["NAME"],
            version=loc["VERSION"],
            description=loc["DESCRIPTION"],
            author=loc["AUTHOR"],
            maintainer=loc["MAINTAINER"],
            url=loc["URL"],
            license=loc["LICENSE"],
            executable_path=executable_path,
        )
    else:
        db_add_new_program(
            name=loc["NAME"],
            version=loc["VERSION"],
            description=loc["DESCRIPTION"],
            author=loc["AUTHOR"],
            maintainer=loc["MAINTAINER"],
            url=loc["URL"],
            license=loc["LICENSE"],
            executable_path=executable_path,
        )

    print(
        Fore.GREEN
        + f"  '{seed}' was installed successfully! The executable file is '{executable_path}'"
    )
    print("  Removing temporary files...")
    shutil.rmtree(temp_dir)


def install_seeds(seeds: List[str], is_forced=False):
    for seed in seeds:
        install_seed(seed, is_forced)


def install_pkg_names(pkg_names: List[str], is_forced=False):
    raise NotImplementedError()
