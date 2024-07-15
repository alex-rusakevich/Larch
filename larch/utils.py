import hashlib
import shutil
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

import requests
from colorama import Fore
from tqdm.auto import tqdm

from larch import LARCH_CACHE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,it;q=0.8,es;q=0.7",
    "Accept-Encoding": "identity",
    "Referer": "https://google.com/",
}

indentation_level = 0
indentation = "  "


def set_print_indentation_lvl(int_lvl: int):
    global indentation_level
    indentation_level = int_lvl


def sp_print(*args, **kwargs):
    global indentation_level

    if kwargs.pop("no_indentation", False) is False:
        print(indentation * indentation_level, end="")

    print(*args, **kwargs)


def str_to_version_tuple(ver: str) -> tuple:
    result = []

    for i in ver.split("."):
        if i.isdigit():
            result.append(int(i))
        else:
            result.append(i)

    return tuple(result)


def hashify(obj: str):
    h = hashlib.new("sha1")
    h.update(obj.encode())
    return h.hexdigest()


def progress_fetch(url: str, dest: Optional[Union[str, BytesIO]], no_cache=False):
    if no_cache:
        with requests.get(
            url,
            stream=True,
            headers=HEADERS,
        ) as r:
            total_length = int(r.headers.get("Content-Length"))

            with tqdm.wrapattr(r.raw, "read", total=total_length) as raw:
                with open(dest, "wb") as output:
                    shutil.copyfileobj(raw, output)

        return

    sp_print(f"Fetching '{url}' to '{dest}'...", end=" ")

    # Try to find in cache
    url_hash = hashify(url)
    possible_cache_file = Path(LARCH_CACHE / url_hash)

    if not possible_cache_file.is_file():
        sp_print()

        with requests.get(
            url,
            stream=True,
            headers=HEADERS,
        ) as r:
            total_length = int(r.headers.get("Content-Length"))

            with tqdm.wrapattr(r.raw, "read", total=total_length) as raw:
                with open(possible_cache_file, "wb") as output:
                    shutil.copyfileobj(raw, output)
    else:
        sp_print(Fore.GREEN + "Using cached", no_indentation=True)

    shutil.copy(possible_cache_file, dest)
    return
    # endregion
