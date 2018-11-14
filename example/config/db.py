"""Database configuration.

For help with the Orator ORM, see the official docs:
https://orator-orm.com

Get started: import the `Model` base class from here and start
building models!
"""
from dotenv import load_dotenv

from bocadillo.db import setup_db

load_dotenv()
db, Model, DATABASES = setup_db(driver='sqlite')
