import platform
from pathlib import Path

import sqlalchemy as db
from colorama import Fore
from sqlalchemy import Column, Integer, String, Table, or_, select

from larch import LARCH_DIR
from larch.update import update_pkg_meta
from larch.utils import sp_print as print

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


def remote_package_exists(pkg_name: str):
    return remote_db_conn.scalars(
        select(RemotePackage).where(RemotePackage.c.name == pkg_name).limit(1)
    ).first()


def get_remote_candidate(pkg_name: str):
    def get_version_tuple(remote_pkg: Table) -> tuple:
        result = []

        for i in remote_pkg.ver.split("."):
            if i.isdigit():
                result.append(int(i))
            else:
                result.append(i)

        return tuple(result)

    current_arch = platform.system() + "_" + platform.architecture()[0]

    candidates = remote_db_conn.execute(
        select(RemotePackage)
        .where(RemotePackage.c.name == pkg_name)
        .where(or_(RemotePackage.c.arch == current_arch, RemotePackage.c.arch == "any"))
    )

    candidates = list(candidates)
    candidates.sort(key=get_version_tuple)

    if candidates is not None:
        return candidates[0]
    else:
        return None
