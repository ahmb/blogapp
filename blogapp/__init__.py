from flask import Flask
from flask.ext.bootstrap import Bootstrap
from .blog import blog as blog_blueprint
from config import config
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

db = SQLAlchemy()
bootstrap = Bootstrap()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # add all the various wrappers here
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)


    app.register_blueprint(blog_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
