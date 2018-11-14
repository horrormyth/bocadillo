import os
from collections import ChainMap
from typing import Optional

from orator import Model, DatabaseManager

from .helpers import remove_nones


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
    env = remove_nones({key: os.getenv(f'db_{key}'.upper()) for key in keys})

    config = ChainMap(args, env, {'driver': 'sqlite'})
    config = {key: config[key] for key in keys if key in config}

    if config['driver'] == 'sqlite':
        config.setdefault('database', 'sqlite.db')

    return {
        alias: config,
    }


def setup_db(
        alias: Optional[str] = 'default',
        driver: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        databases: Optional[dict] = None,
):
    """Configure an Orator database.

    When called without any parameters, this will configure a
    SQLite database called 'sqlite.db'.

    Parameters
    ----------
    alias : str, optional
        Alias for the database configuration.
        Defaults to 'default'.
    driver : str, optional
        Orator database driver used.
        One of: 'sqlite', 'pgsql', 'mysql'.
        Defaults to $DB_DRIVER or 'sqlite'.
    database : str, optional
        The name of the database.
        Defaults to $DB_NAME, or 'sqlite.db' (if using the sqlite driver).
    user : str, optional
        The name of the user on the database.
        Defaults to $DB_USER or None.
    password : str, optional
        The password used to access the database.
        Defaults to $DB_PASSWORD or None.
    host : str, optional
        The host where the database is accessible.
        Defaults to $DB_HOST or None.
    port : str, optional
        The port on which the database is accessible.
        Defaults to $DB_PORT or None.
    databases : dict, optional
        An explicit configuration dictionary for advanced usages
        (e.g. multiple databases).
        Defaults to None.

    See Also
    --------
    Orator ORM configuration :
        https://orator-orm.com/docs/0.9/basic_usage.html#configuration
    """
    if databases is None:
        databases = make_db_config(
            alias=alias,
            driver=driver,
            database=database,
            user=user,
            password=password,
            host=host,
            port=port,
        )

    db = DatabaseManager(databases)
    Model.set_connection_resolver(db)
    return db, Model, databases
