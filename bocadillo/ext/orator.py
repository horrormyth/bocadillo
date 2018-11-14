import os
from collections import ChainMap

from ..helpers import remove_nones

# Aliases

try:
    import orator
    from orator import DatabaseManager
    from orator import Model
    from orator.migrations import Migration
except ImportError as e:
    raise ImportError(
        'Cannot configure databases: Orator is not installed. '
        'Hint: run `pip install bocadillo[db]`.'
    ) from e


# Orator ORM configuration helpers
# See also:
# https://orator-orm.com/docs/0.9/orm.html#basic-usage

def configure(databases: dict = None) -> DatabaseManager:
    if databases is None:
        databases = {}
    db = DatabaseManager(databases)
    Model.set_connection_resolver(db)
    return db


def make_db_config(alias: str = 'default', **kwargs) -> dict:
    keys = (
        'driver',
        'database',
        'user',
        'password',
        'host',
        'port',
    )

    args = remove_nones({key: kwargs.get(key) for key in keys})
    env = remove_nones({key: os.getenv('db_{key}'.upper()) for key in keys})

    config = ChainMap(args, env, {'driver': 'sqlite'})
    config = {key: config[key] for key in keys if key in config}

    if config['driver'] == 'sqlite':
        config.setdefault('database', 'sqlite.db')

    return {
        alias: config,
    }
