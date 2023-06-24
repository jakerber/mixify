"""Application configuration."""
import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())  # load from .env

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
