from dotenv import load_dotenv

from bocadillo.db import setup_db

load_dotenv()
db, Model, DATABASES = setup_db()
