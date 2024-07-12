import os.path
import shutil
import zipfile
from colorama import Fore


def join_path(*args):
    return os.path.abspath(os.path.join(*args))


def unzip(archive: str, dest_folder: str):
    print(f"  Unpacking '{archive}' to '{dest_folder}'...", end=" ")

    with zipfile.ZipFile(archive, "r") as zip_ref:
        zip_ref.extractall(dest_folder)

    print(Fore.GREEN + "Done")


def copy(src: str, dst: str):
    print(f"  Copying '{src}' to '{dst}'...", end=" ")

    shutil.copytree(src, dst, dirs_exist_ok=True)

    print(Fore.GREEN + "Done")
