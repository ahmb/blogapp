from flask import render_template, current_app, request, redirect, url_for, \
    flash, g
from flask.ext.login import login_user, logout_user, login_required
from ..models import User
from . import auth
from .forms import LoginForm, RegistrationForm
from .forms import SearchForm
from flask.ext.login import login_required, current_user

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if not current_app.config['DEBUG'] and not current_app.config['TESTING']:
    #and not request.is_secure:

        return redirect(url_for('.login', _external=True, _scheme='https'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.verify_password(form.password.data):

            flash('Invalid email or password.')
            #the **request.args is used to send the "next" page data from the client to the server so the client can be redirected there after logging the client in
            return redirect(url_for('.login', **request.args))

        login_user(user, form.remember_me.data)
        return redirect(request.args.get('next') or url_for('blog.index'))

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('blog.index'))

@auth.route('/signup', methods=['GET','POST'])
def register():
    form = RegistrationForm()

@auth.before_request
def before_request():
    g.user = current_user
    g.search_form = SearchForm()
