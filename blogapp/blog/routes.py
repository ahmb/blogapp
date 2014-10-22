from flask import render_template, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from .. import db
from . import blog
from ..models import User, BlogPost
from .forms import ProfileForm, BlogPostForm

@blog.route('/')
def index():
    blogpost_list = BlogPost.query.order_by(BlogPost.date.desc()).all()
    return render_template('blog/index.html', blogposts=blogpost_list)

@blog.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    blogpost_list = user.blogpost.order_by(BlogPost.date.desc()).all()
    return render_template('blog/user.html', user=user, blogposts=blogpost_list)

@blog.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('blog.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template('blog/profile.html', form=form)

@blog.route('/new', methods=['GET', 'POST'])
@login_required
def new_blogpost():
    form = BlogPostForm()
    if form.validate_on_submit():
        blogpost = BlogPost(title=form.title.data,
                    description=form.description.data,
                    slides=form.slides.data,
                    video=form.video.data,
                    venue=form.venue.data,
                    venue_url=form.venue_url.data,
                    date=form.date.data,
                    author=current_user)
        db.session.add(blogpost)
        db.session.commit()
        flash('The blog post was added successfully.')
        return redirect(url_for('.index'))
    return render_template('blog/edit_blogpost.html', form=form)
