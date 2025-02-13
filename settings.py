import os

from environs import Env

env = Env()


class Config(object):
    """Base configuration."""

    # configure log level from environment variable
    log_level_names = {
        "CRITICAL",
        "FATAL",
        "ERROR",
        "WARN",
        "WARNING",
        "INFO",
        "DEBUG",
        "NOTSET",
    }

    LOG_LEVEL = env("LOG_LEVEL", "INFO").upper()
    if LOG_LEVEL not in log_level_names:
        print(
            f"LOG_LEVEL is invalid, valid levels are: {log_level_names} \n\tWill use `INFO` instead."
        )
        LOG_LEVEL = "INFO"

    APP_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir)
    )  # This directory

    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # Debug
    DEBUG = env.bool("FLASK_DEBUG", True)

    TIME_ZONE = "Asia/Singapore"

    # Data admin Postgres
    POSTGRES_HOSTNAME = env("POSTGRES_HOSTNAME", default="")
    POSTGRES_PORT = env.int("POSTGRES_PORT", default=5432)
    POSTGRES_DB = env("POSTGRES_DB", default="")
    POSTGRES_USER = env("POSTGRES_USER", default="")
    POSTGRES_PASSWORD = env("POSTGRES_PASSWORD", default="")
    READ_ONLY = env.bool("READ_ONLY", False)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "execution_options": {"postgresql_readonly": READ_ONLY},
    }
    DEVAEGIS_DATABASE_URI = env(
        "SQLALCHEMY_DATABASE_URI",
        default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOSTNAME}:{POSTGRES_PORT}/{POSTGRES_DB}",
    )

    # Bind DB to name
    SQLALCHEMY_BINDS = {
        "devaegis_db": DEVAEGIS_DATABASE_URI,
    }

    APP_DATA_URL_PREFIX = env("APP_DATA_URL_PREFIX", "/api/v1")

    os.environ["OPENAI_API_KEY"] = env(
        "OPENAI_API_KEY",
        "",
    )

    AUTH_TOKEN = env("AUTH_TOKEN")
