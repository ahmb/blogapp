from flask import render_template
from . import blog


@blog.route('/')
def index():
    return render_template('blog/index.html')


@blog.route('/user/<username>')
def user(username):
    return render_template('blog/user.html', username=username)