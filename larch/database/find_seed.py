import os
from pathlib import Path
from typing import Optional

from sqlalchemy import select

from larch import LARCH_PROG_DIR, LARCH_REPO, LARCH_TEMP
from larch.database.local import LocalPackage, local_db_conn
from larch.database.remote import get_remote_candidate
from larch.utils import progress_fetch, str_to_version_tuple


class FoundSeed:
    class FoundSeedType:
        INSTALLED = 0
        REMOTE = 1

    seed_code = ""
    seed_type = None

    def __init__(self, seed_code, seed_type) -> None:
        self.seed_code = seed_code
        self.seed_type = seed_type


def find_seed_in_installed(
    pkg_name: str, pkg_comp_str: Optional[str], pkg_ver: Optional[tuple]
) -> Optional[FoundSeed]:
    local_packages = list(
        local_db_conn.execute(
            select(LocalPackage).where(LocalPackage.c.name == pkg_name)
        )
    )
    local_packages.sort(key=lambda x: str_to_version_tuple(x.version))

    if pkg_comp_str and pkg_ver:
        comp_func = {
            "==": pkg_ver.__eq__,
            ">=": pkg_ver.__ge__,
            "<=": pkg_ver.__le__,
            ">": pkg_ver.__gt__,
            "<": pkg_ver.__lt__,
            "!=": pkg_ver.__ne__,
        }[pkg_comp_str]

        if pkg_comp_str and pkg_ver:
            local_packages = list(
                filter(
                    lambda pkg: comp_func(str_to_version_tuple(pkg.version)),
                    local_packages,
                )
            )

    if len(local_packages) == 0:
        return None
    else:
        return FoundSeed(
            seed_code=Path(LARCH_PROG_DIR, pkg_name, "larchseed.py").read_text(),
            seed_type=FoundSeed.FoundSeedType.INSTALLED,
        )


def find_seed(
    pkg_name: str, pkg_comp_str: Optional[str], pkg_ver: Optional[tuple]
) -> Optional[FoundSeed]:
    # region Find in installed
    installed_seed = find_seed_in_installed(pkg_name, pkg_comp_str, pkg_ver)

    if installed_seed:
        return installed_seed
    # endregion

    # region Find in remote
    remote_pkg = get_remote_candidate(pkg_name, (pkg_comp_str, pkg_ver))

    if remote_pkg:
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

        return FoundSeed(
            seed_code=Path(seed_path).read_text(),
            seed_type=FoundSeed.FoundSeedType.REMOTE,
        )
    else:
        return None
    # endregion
