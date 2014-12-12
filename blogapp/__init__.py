from flask import Flask, jsonify, g
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.moment import Moment
from flask.ext.pagedown import PageDown
from flask.ext.mail import Mail
from config import *
#from flask.ext.babel import Babel


db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

mail = Mail()

moment = Moment()

pagedown = PageDown()

bootstrap = Bootstrap()


#babel = Babel()

def create_app(config_name):
    app = Flask(__name__)
    #app.config.from_object(config[config_name])
    app.config.from_object(DevelopmentConfig)


    db.init_app(app)

    #babel.init_app(app)

    Mail(app)

    bootstrap.init_app(app)

    moment.init_app(app)

    pagedown.init_app(app)

    login_manager.init_app(app)

    #with app.app_context():
        # Extensions like Flask-SQLAlchemy now know what the "current" app
        # is while within this block. Therefore, you can now run........
        #db.drop_all()
    #    db.create_all()

    from .blog import blog as blog_blueprint
    app.register_blueprint(blog_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .api_1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/1.0')

    from .errors import errors as errors_blueprint
    app.register_blueprint(errors_blueprint, url_prefix='/error')



    return app

