import os

from dotenv import load_dotenv, find_dotenv

def load():
    """
    Load Environment Files (e.g. .env, .env.development.local, .env.production, etc.).
    :return: None
    """
    # Load .env files

    pyenv = os.getenv("PYTHON_ENV", "development")

    load_dotenv(find_dotenv(f".env.{pyenv}.local"), verbose=True)
    load_dotenv(find_dotenv(f".env.{pyenv}"), verbose=True)

    load_dotenv(find_dotenv(), verbose=True, override=True)


load()
