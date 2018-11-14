import os
import sqlite3

import pytest

from bocadillo.db import setup_db


@pytest.mark.parametrize('given, expected', [
    (
            {},
            {
                'alias': 'default',
                'database': 'sqlite.db',
            },
    ),
    (
            {
                'alias': 'my_db',
            },
            {
                'alias': 'my_db',
                'database': 'sqlite.db',
            },
    ),
    (
            {
                'database': 'my_sqlite.db',
            },
            {
                'alias': 'default',
                'database': 'my_sqlite.db',
            },
    ),
    (
            {
                'databases': {
                    'my_db': {
                        'driver': 'sqlite',
                        'database': 'my_sqlite.db',
                    },
                },
            },
            {
                'alias': 'my_db',
                'database': 'my_sqlite.db',
            }
    )
])
def test_setup_sqlite_db(given: dict, expected: dict):
    db, Model, DATABASES = setup_db(**given)
    conn = db.connection()
    try:
        assert conn.get_name() == expected['alias']
        assert conn.get_database_name() == expected['database']
        assert conn.get_connection().get_api() == sqlite3
    finally:
        conn.disconnect()
        os.remove(expected['database'])
