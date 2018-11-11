import os
import sqlite3

import pytest

from bocadillo import API


@pytest.mark.parametrize('given, expected', [
    (
            {},
            {
                'alias': 'default',
                'name': 'sqlite.db',
            },
    ),
    (
            {
                'alias': 'my_db',
            },
            {
                'alias': 'my_db',
                'name': 'sqlite.db',
            },
    ),
    (
            {
                'name': 'my_sqlite.db',
            },
            {
                'alias': 'default',
                'name': 'my_sqlite.db',
            },
    ),
])
def test_setup_sqlite_db(api: API, given: dict, expected: dict):
    api.setup_orator(**given)
    conn = api.db.connection()
    try:
        assert conn.get_name() == expected['alias']
        assert conn.get_database_name() == expected['name']
        assert conn.get_connection().get_api() == sqlite3
    finally:
        conn.disconnect()
        os.remove(expected['name'])
