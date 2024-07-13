from pathlib import Path

import sqlalchemy as db
from sqlalchemy import Column, Integer, String, Table, Text, select, text

from larch import LARCH_DIR

LARCH_INSTALLED_DB = Path(LARCH_DIR) / "local.db"

local_db_engine = db.create_engine(f"sqlite:///{LARCH_INSTALLED_DB}")
local_db_conn = local_db_engine.connect()

metadata = db.MetaData()

Program = Table(
    "programs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False, unique=True),
    Column("version", String, nullable=False),
    Column("description", Text, nullable=False),
    Column("author", String, nullable=False),
    Column("maintainer", String, nullable=False),
    Column("url", String, nullable=False),
    Column("license", String, nullable=False),
    Column("executable", String, nullable=False),
)

metadata.create_all(local_db_engine)

local_db_conn.execute(text("PRAGMA auto_vacuum = 1;"))
local_db_conn.commit()


def program_installed(prog_name) -> bool:
    return local_db_conn.scalars(
        select(Program).where(Program.c.name == prog_name).limit(1)
    ).first()
