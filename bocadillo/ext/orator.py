import os
from collections import ChainMap
from importlib import import_module

from ..helpers import remove_nones

# Aliases

try:
    import orator
    from orator import DatabaseManager
    from orator import Model
    from orator.migrations import Migration
except ImportError:
    DatabaseManager = None
    Model = None
    Migration = None

DEFAULT_DRIVER = 'sqlite'
DEFAULT_DB_NAME = 'sqlite.db'
DEFAULT_ALIAS = 'default'


# Orator ORM configuration helpers
# See also:
# https://orator-orm.com/docs/0.9/orm.html#basic-usage

def configure(databases: dict = None) -> DatabaseManager:
    assert DatabaseManager is not None, (
        'Cannot configure databases: orator not installed'
    )
    if databases is None:
        databases = {}
    db = DatabaseManager(databases)
    Model.set_connection_resolver(db)
    return db


def configure_from_module(module: str) -> DatabaseManager:
    databases: dict = import_module(module).DATABASES
    return configure(databases=databases)


def configure_one(alias: str, **kwargs) -> DatabaseManager:
    databases = make_db_config(alias, **kwargs)
    return configure(databases=databases)


def make_db_config(alias: str = DEFAULT_ALIAS, **kwargs) -> dict:
    keys = (
        'driver',
        'database',
        'user',
        'password',
        'host',
        'port',
    )
    kwargs.setdefault('driver', DEFAULT_DRIVER)
    kwargs.setdefault('database', DEFAULT_DB_NAME)

    args = remove_nones({key: kwargs.get(key) for key in keys})
    env = remove_nones({key: os.getenv('db_{key}'.upper()) for key in keys})

    config = ChainMap(args, env)
    config = {key: config[key] for key in keys if key in config}

    return {
        alias: config,
    }
