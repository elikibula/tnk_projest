"""Online, non-overwriting full SQLite backup using the selected Django settings."""
import argparse
from contextlib import closing
import os
from pathlib import Path
import sqlite3
import sys


def backup_sqlite(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination:
        raise ValueError("Backup must not overwrite the source database.")
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as reader:
        # Exclusive creation refuses existing backups, source files and symlinks.
        with destination.open("xb"):
            pass
        writer = sqlite3.connect(destination)
        try:
            reader.backup(writer)
            if writer.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("Backup integrity check failed; do not use this backup.")
        finally:
            writer.close()
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", default="config.settings.local")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
    os.environ["DJANGO_SETTINGS_MODULE"] = args.settings
    import django
    django.setup()
    from django.db import connection
    if connection.vendor != "sqlite" or connection.settings_dict["NAME"] == ":memory:":
        parser.error("This command backs up file-based SQLite only; use pg_dump for production PostgreSQL.")
    try:
        result = backup_sqlite(connection.settings_dict["NAME"], args.output)
    except (OSError, ValueError, sqlite3.Error, RuntimeError) as error:
        parser.exit(1, f"Backup failed: {error}\nAn incomplete destination, if created, is retained for inspection.\n")
    print(f"Verified full database backup: {result}")


if __name__ == "__main__":
    main()
