import os
import shutil

from colorama import Fore

from larch import LARCH_CACHE
from larch.utils import set_print_indentation_lvl
from larch.utils import sp_print as print


def get_folder_size(folder_path: str):
    total_size = 0

    for path, _, files in os.walk(folder_path):
        for f in files:
            fp = os.path.join(path, f)
            total_size += os.path.getsize(fp)

    return total_size


def clear_cache():
    set_print_indentation_lvl(0)
    print("Clearing the cached downloads...")

    set_print_indentation_lvl(1)

    print("Calculating the cache size...", end=" ")
    total_cache_size = get_folder_size(str(LARCH_CACHE)) / (1024**2)
    print(Fore.GREEN + "OK", no_indentation=True)

    print("Removing cache files...", end=" ")
    shutil.rmtree(LARCH_CACHE)
    print(Fore.GREEN + "OK", no_indentation=True)

    print(Fore.GREEN + f"Done! Removed {total_cache_size:.2f} MB data!")
