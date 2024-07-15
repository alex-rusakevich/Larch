import os
import os.path
import shutil
import subprocess
import sys
import zipfile

from colorama import Fore

from larch.utils import sp_print as print

restricted_dirs = []


def validate_path(path: str):
    norm_path = os.path.abspath(os.path.normpath(path))
    global restricted_dirs

    if restricted_dirs:
        for restricted_dir in restricted_dirs:
            restricted_dir = os.path.abspath(os.path.normpath(restricted_dir))

            if norm_path.startswith(restricted_dir):
                return

        print(
            Fore.RED
            + f"larchseed.py attempted to access a path outside of destination and temp dirs: '{path}'"
        )
        sys.exit(1)


def join_path(*args):
    return os.path.join(*args)


def unzip(archive: str, dest_folder: str):
    validate_path(archive)
    validate_path(dest_folder)

    print(f"Unpacking '{archive}' to '{dest_folder}'...", end=" ")

    with zipfile.ZipFile(archive, "r") as zip_ref:
        zip_ref.extractall(dest_folder)

    print(Fore.GREEN + "Done", no_indentation=True)


def copytree(src: str, dst: str):
    validate_path(src)
    validate_path(dst)

    print(f"Copying '{src}' to '{dst}'...", end=" ")

    shutil.copytree(src, dst, dirs_exist_ok=True)

    print(Fore.GREEN + "Done", no_indentation=True)


def copyfile(src: str, dst: str):
    validate_path(src)
    validate_path(dst)

    print(f"Copying '{src}' to '{dst}'...", end=" ")

    shutil.copy2(src, dst)

    print(Fore.GREEN + "Done", no_indentation=True)


def run(command: str, *args):
    print(f"Running '{command}{''.join(' ' + i for i in args)}'")
    subprocess.run([command, *args])
