from flask import render_template
from . import blog
from ..models import User

@blog.route('/')
def index():
    return render_template('blog/index.html')


@blog.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('blog/user.html', user=user)