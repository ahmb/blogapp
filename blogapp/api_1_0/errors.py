from flask import jsonify
from . import api
from ..exceptions import ValidationError


@api.errorhandler(ValidationError)
def bad_request(message):
    response = jsonify({'status': 'bad request', 'message': message})
    response.status_code = 400
    return response

@api.errorhandler(404)
def unauthorized(message):
    response = jsonify({'status': 'unauthorized', 'message': message})
    response.status_code = 401
    return response

@api.errorhandler(405)
def forbidden(message):
    response = jsonify({'status': 'forbidden', 'message': message})
    response.status_code = 403
    return response
'''
The code below doesnt work because of :
AssertionError: It is currently not possible to register a 500 internal server error on a per-blueprint level.


@api.app_errorhandler(500)
def internal_server_error(e):
    response = jsonify({'status': 500, 'error': 'internal server error'})
    response.status_code = 500
    return response
'''

#below is an application scope error handler
@api.app_errorhandler(404)
def not_found(message):
    response = jsonify({'status': 'not found', 'message': message})
    response.status_code = 404
    return response

