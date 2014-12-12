from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes

__author__ = 'Ahmad'

from flask import jsonify, g, current_app
from flask.ext.httpauth import HTTPBasicAuth
from ..models import User

authx = HTTPBasicAuth()
auth_token = HTTPBasicAuth()


@authx.verify_password
def verify_password(username, password):
    g.user = User.query.filter_by(username=username).first()
    if g.user is None:
        return False
    return g.user.verify_password(password)

@authx.error_handler
def unauthorized():
    response = jsonify({'status': 401, 'error': 'unauthorized',
                        'message': 'please authenticate'})
    response.status_code = 401
    return response

@auth_token.verify_password
#unused is unused for tokens but is used for passwords; client can either choose to send token or username and password< Currently the workflow mandates that the client get the token from a route before being able to utilize it
def verify_auth_token(token, unused):
    if current_app.config.get('IGNORE_AUTH') is True:
        g.user = User.query.get(1)
    else:
        #including both
        g.user = User.verify_auth_token(token) or verify_password(token, unused)
    return g.user is not None

@auth_token.error_handler
def unauthorized_token():
    response = jsonify({'status': 401, 'error': 'unauthorized',
                        'message': 'please send your authentication token'})
    response.status_code = 401
    return response