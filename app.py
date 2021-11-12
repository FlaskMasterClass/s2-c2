import os
import pathlib

import click
import flask
from flask import Flask
from flask import current_app
from flask.cli import load_dotenv

from init import db
from init import migrate

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


from config import DevelopmentConfig
from config import ProductionConfig
from config import TestingConfig

profiles = {
    "development": DevelopmentConfig(),
    "production": ProductionConfig(),
    "testing": TestingConfig(),
}


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


def create_app(profile):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(profiles[profile])
    app.config.from_pyfile("config.py", silent=True)

    db.init_app(app)
    migrate.init_app(app, db)

    if profile != "testing":
        app.config.from_pyfile("config.py", silent=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.shell_context_processor
    def shell():
        return {
            "db": db,
        }

    return app


flask_env = os.environ.get("FLASK_ENV", default="development")
app = create_app(flask_env)

if __name__ == "__main__":
    app.run()
