import sqlite3
from pathlib import Path

from larch import LARCH_DIR

LARCH_INSTALLED_DB = Path(LARCH_DIR) / "installed.db"

connection = sqlite3.connect(LARCH_INSTALLED_DB)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Programs (
    id INTEGER PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE,
    version VARCHAR(64) NOT NULL,
    description TEXT NOT NULL,

    author TEXT NOT NULL,
    maintainer TEXT NOT NULL,
    url TEXT NOT NULL,
    license TEXT NOT NULL,
    executable_path VARCHAR(256) NOT NULL
)
"""
)

cursor.execute(
    """
    PRAGMA auto_vacuum = 1;
"""
)

connection.commit()


def db_get_program_by_name(name):
    c = cursor.execute("SELECT * FROM Programs WHERE name = ?", (name,))
    data = c.fetchone()

    return data


def db_program_exists(name):
    data = db_get_program_by_name(name)

    if data is None:
        return False
    else:
        return True


def db_upsert_program(name, version, **kwargs):
    version = ".".join(str(i) for i in version)

    if not db_program_exists(name):
        cursor.execute(
            f"""INSERT INTO Programs (name, version, {', '.join(kwargs.keys())})
                VALUES (?, ?, {', '.join(len(kwargs.keys()) * '?')})""",
            (name, version, *kwargs.values()),
        )
    else:
        set_keys = ", ".join(f"{key} = ?" for key in kwargs.keys())

        cursor.execute(
            f"""UPDATE Programs
                SET name = ?, version = ?, {set_keys}
                WHERE name = ?""",
            (name, version, *kwargs.values(), name),
        )

    connection.commit()


def db_remove_program(name):
    cursor.execute("DELETE FROM Programs WHERE name = ?", (name,))
    connection.commit()


def db_list_installed():
    cursor.execute("SELECT * FROM Programs ORDER BY name")
    results = cursor.fetchall()
    return results
