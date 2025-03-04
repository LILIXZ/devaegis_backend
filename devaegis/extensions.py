"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ma = Marshmallow()
