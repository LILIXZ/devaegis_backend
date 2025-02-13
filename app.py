import logging
import sys

from flask import Flask
from flask_cors import CORS

from settings import Config
from views import search_views

logger = logging.getLogger(__name__)


def get_config():
    app_config = Config
    logger.debug(f"Initialize config successfully")
    return app_config


def register_blueprints(app):
    """Register Flask blueprints."""
    app_data_url_prefix = app.config["APP_DATA_URL_PREFIX"]
    app.register_blueprint(
        search_views.blueprint, url_prefix=f"{app_data_url_prefix}/search"
    )
    pass


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


def create_app():
    config_object = get_config()
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(config_object)
    register_blueprints(app)
    configure_logger(app)

    return app


app = create_app()
