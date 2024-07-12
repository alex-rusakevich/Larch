from typing import Optional
import requests
import shutil
import hashlib
from tqdm.auto import tqdm
from larch import LARCH_CACHE
from pathlib import Path


def hashify(obj: str):
    h = hashlib.new("sha256")
    h.update(obj.encode())
    return h.hexdigest()


def progress_fetch(url: str, dest: Optional[str]):
    print(f"Downloading '{url}' to '{dest}'...", end=" ")

    # Try to find in cache
    url_hash = hashify(url)
    possible_cache_file = Path(LARCH_CACHE / url_hash)

    if not possible_cache_file.is_file():
        print()

        with requests.get(url, stream=True) as r:
            total_length = int(r.headers.get("Content-Length"))

            with tqdm.wrapattr(r.raw, "read", total=total_length) as raw:
                with open(possible_cache_file, "wb") as output:
                    shutil.copyfileobj(raw, output)
    else:
        print("Used cached")

    shutil.copy(possible_cache_file, dest)
    return
    # endregion
