import os
from datetime import datetime, timezone

import requests
from colorama import Fore
from dateutil import parser

from larch import LARCH_DIR, LARCH_REPO
from larch.cli import progress_fetch
from larch.utils import HEADERS, set_print_indentaion_lvl
from larch.utils import sp_print as print


def get_remote_timestamp():
    print("Getting remote timestamp...", end=" ")
    r = requests.get(LARCH_REPO + ".remote-db-timestamp", headers=HEADERS)
    timestamp = r.content.decode("utf-8")

    print(Fore.GREEN + "OK", no_indentation=True)

    return parser.parse(timestamp.strip())


def fetch_remote_db():
    print("Fetching remote package info...")
    progress_fetch(LARCH_REPO + "remote.db", LARCH_DIR / "remote.db", no_cache=True)


def update_pkg_meta(is_forced=False):
    set_print_indentaion_lvl(0)

    if is_forced:
        print(Fore.YELLOW + "Forcefully updating remote repository information...")
    else:
        print("Updating remote repository information...")

    set_print_indentaion_lvl(1)

    remote_timestamp = get_remote_timestamp()

    if (
        os.path.isfile(LARCH_DIR / ".remote-db-timestamp")
        and os.path.isfile(LARCH_DIR / "remote.db")
        and remote_timestamp <= datetime.now(timezone.utc)
        and not is_forced
    ):
        print(Fore.YELLOW + "remote.db is already up-to-date, stopping")
    else:
        fetch_remote_db()

        print("Updating local remote.db timestamp...", end=" ")
        with open(LARCH_DIR / ".remote-db-timestamp", "w", encoding="utf8") as f:
            f.write(str(remote_timestamp))
            f.write("\n")
        print(Fore.GREEN + "OK", no_indentation=True)

        print(Fore.GREEN + "Update procedure has been completed successfully.")

    set_print_indentaion_lvl(0)
