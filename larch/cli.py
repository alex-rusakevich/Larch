import hashlib
import shutil
from pathlib import Path
from typing import Optional

import requests
from colorama import Fore
from tqdm.auto import tqdm

from larch import LARCH_CACHE
from larch.utils import sp_print as print


def hashify(obj: str):
    h = hashlib.new("sha1")
    h.update(obj.encode())
    return h.hexdigest()


def progress_fetch(url: str, dest: Optional[str]):
    print(f"Downloading '{url}' to '{dest}'...", end=" ")

    # Try to find in cache
    url_hash = hashify(url)
    possible_cache_file = Path(LARCH_CACHE / url_hash)

    if not possible_cache_file.is_file():
        print()

        with requests.get(
            url,
            stream=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9,it;q=0.8,es;q=0.7",
                "Accept-Encoding": "identity",
                "Referer": "https://google.com/",
            },
        ) as r:
            total_length = int(r.headers.get("Content-Length"))

            with tqdm.wrapattr(r.raw, "read", total=total_length) as raw:
                with open(possible_cache_file, "wb") as output:
                    shutil.copyfileobj(raw, output)
    else:
        print(Fore.GREEN + "Using cached", no_indentation=True)

    shutil.copy(possible_cache_file, dest)
    return
    # endregion
