from larch import LARCH_DIR
import sqlite3
from pathlib import Path

LARCH_INSTALLED_DB = Path(LARCH_DIR) / "installed.db"

connection = sqlite3.connect(LARCH_INSTALLED_DB)
cursor = connection.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Programs (
    id INTEGER PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE,
    version VARCHAR(32) NOT NULL,
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


def db_add_new_program(
    name, version, description, author, maintainer, url, license, executable_path
):
    version = ".".join(str(i) for i in version)

    cursor.execute(
        """INSERT INTO Programs (name, version, description, author, maintainer, url, license, executable_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            name,
            version,
            description,
            author,
            maintainer,
            url,
            license,
            str(executable_path),
        ),
    )

    connection.commit()


def db_program_exists(name):
    cursor.execute("SELECT * FROM Programs WHERE name = ?", (name,))
    data = cursor.fetchone()

    if data is None:
        return False
    else:
        return True


def db_remove_program(name):
    cursor.execute("DELETE FROM Programs WHERE name = ?", (name,))
    connection.commit()
