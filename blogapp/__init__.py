from flask import Flask
from flask.ext.bootstrap import Bootstrap
from .blog import blog as blog_blueprint
from config import config
from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()
bootstrap = Bootstrap()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # add all the various wrappers here
    bootstrap.init_app(app)
    db.init_app(app)



    app.register_blueprint(blog_blueprint)

    return app
