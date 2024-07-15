from pathlib import Path

import sqlalchemy as db
from sqlalchemy import Column, Integer, String, Table, Text, select, text

from larch import LARCH_DIR

LARCH_INSTALLED_DB = Path(LARCH_DIR) / "local.db"

local_db_engine = db.create_engine(f"sqlite:///{LARCH_INSTALLED_DB}")
local_db_conn = local_db_engine.connect()

metadata = db.MetaData()

LocalPackage = Table(
    "packages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, unique=True),
    Column("version", String, nullable=False),
    Column("description", Text, nullable=False),
    Column("author", String, nullable=False),
    Column("maintainer", String, nullable=False),
    Column("url", String, nullable=False),
    Column("license", String, nullable=False),
    Column("entry_point", String, nullable=True),
)

metadata.create_all(local_db_engine)

local_db_conn.execute(text("PRAGMA auto_vacuum = 1;"))
local_db_conn.commit()


def package_installed(pkg_name) -> bool:
    return local_db_conn.scalars(
        select(LocalPackage).where(LocalPackage.c.name == pkg_name).limit(1)
    ).first()


def get_installed_pkg_by_name(pkg_name):
    return local_db_conn.execute(
        select(LocalPackage).where(LocalPackage.c.name == pkg_name)
    ).one_or_none()
