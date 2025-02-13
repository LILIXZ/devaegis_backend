import logging
import os
import sys

from flask import Flask
from flask_caching import Cache
from flask_cors import CORS

from cli_management_commands.cli_db_management import database_healthcheck
from extensions import db, ma
from settings import Config
from views import search_views

logger = logging.getLogger(__name__)


def get_config():
    app_config = Config
    logger.debug(f"Initialize config successfully")
    return app_config


def register_extensions(app):
    """Register Flask extensions."""
    cache = Cache()

    cache.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    return


def register_blueprints(app):
    """Register Flask blueprints."""
    app_data_url_prefix = app.config["APP_DATA_URL_PREFIX"]
    app.register_blueprint(
        search_views.blueprint, url_prefix=f"{app_data_url_prefix}/search"
    )
    pass


def register_shell_context(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db}

    app.shell_context_processor(shell_context)


def register_cli_commands(app):
    app.cli.add_command(database_healthcheck)


def configure_logger(app):
    # get logger level from settings
    log_level = app.config["LOG_LEVEL"]

    """Configure loggers."""
    default_format = logging.Formatter(
        "%(asctime)s - data_center - %(levelname)s - %(message)s - [in %(pathname)s:%(lineno)d]"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(default_format)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
    # if app.config["ENV"] == PROD:
    #     gunicorn_logger = logging.getLogger("gunicorn.error")
    #     app.logger.handlers = gunicorn_logger.handlers
    #     app.logger.setLevel(log_level)


def create_app():
    config_object = get_config()
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_shell_context(app)
    register_cli_commands(app)
    configure_logger(app)

    return app


app = create_app()
