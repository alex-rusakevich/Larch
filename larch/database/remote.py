import platform
from pathlib import Path
from typing import Optional, Tuple

import sqlalchemy as db
from colorama import Fore
from sqlalchemy import Column, Integer, String, Table, or_, select

from larch import LARCH_DIR
from larch.update import update_pkg_meta
from larch.utils import sp_print as print
from larch.utils import str_to_version_tuple

LARCH_REMOTE_DB = Path(LARCH_DIR) / "remote.db"

if not LARCH_REMOTE_DB.is_file():
    print(Fore.YELLOW + "Missing remote.db, running larch.py update...")
    update_pkg_meta()

remote_db_engine = db.create_engine(f"sqlite:///{LARCH_REMOTE_DB}")
remote_db_conn = remote_db_engine.connect()

metadata = db.MetaData()

RemotePackage = Table(
    "packages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, unique=True),
    Column("ver", String, nullable=False),
    Column("arch", String, nullable=False),
)

RemotePkgMeta = Table(
    "pkg_meta",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, unique=True),
    Column("desc", String, nullable=False),
)


def remote_package_exists(pkg_name: str):
    return remote_db_conn.scalars(
        select(RemotePackage).where(RemotePackage.c.name == pkg_name).limit(1)
    ).first()


def get_remote_candidate(pkg_name: str, desired_ver: Optional[Tuple[str, str]]):
    def candidate_version_suits(candidate):
        operation, desired_ver_tuple = desired_ver[0], str_to_version_tuple(
            desired_ver[1]
        )
        candidate_ver = str_to_version_tuple(candidate.ver)

        compare_candidate_to = {
            "==": candidate_ver.__eq__,
            ">=": candidate_ver.__ge__,
            "<=": candidate_ver.__le__,
            ">": candidate_ver.__gt__,
            "<": candidate_ver.__lt__,
        }[operation]

        return compare_candidate_to(desired_ver_tuple)

    current_arch = platform.system() + "_" + platform.architecture()[0]

    candidates = remote_db_conn.execute(
        select(RemotePackage)
        .where(RemotePackage.c.name == pkg_name)
        .where(or_(RemotePackage.c.arch == current_arch, RemotePackage.c.arch == "any"))
    )

    candidates = list(candidates)
    candidates.sort(key=lambda x: str_to_version_tuple(x.ver))

    if desired_ver is not None:
        candidates = list(filter(candidate_version_suits, candidates))

    if candidates not in [None, [], ()]:
        return candidates[0]
    else:
        return None
