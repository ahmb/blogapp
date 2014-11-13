from flask import render_template, flash, redirect, url_for, abort,\
    request, current_app, g
from .. import db
from . import errors
'''
@errors.app_errorhandler(404)
def not_found_error(error):
    return render_template('blog/404.html'), 404


@errors.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('blog/500.html'), 500

@errors.app_errorhandler(Exception)
def catchall_exception(error):
    return render_template('blog/500.html'), 500
'''