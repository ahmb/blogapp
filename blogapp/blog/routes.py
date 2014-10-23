from flask import render_template, flash, redirect, url_for, abort
from flask.ext.login import login_required, current_user
from .. import db
from . import blog
from ..models import User, BlogPost, Comment
from .forms import ProfileForm, BlogPostForm, CommentForm, PresenterCommentForm

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
        #OR try the 2 line code below instead:
        #blogpost = BlogPost(author=current_user)
        #form.to_model(blogpost)
        db.session.add(blogpost)
        db.session.commit()
        flash('The blog post was added successfully.')
        return redirect(url_for('.index'))
    return render_template('blog/edit_blogpost.html', form=form)

@blog.route('/blogpost/<int:id>', methods=['GET', 'POST'])
def getblogpost(id):
    blogpost = BlogPost.query.get_or_404(id)
    comment = None
    if current_user.is_authenticated():
        form = PresenterCommentForm()
        if form.validate_on_submit():
            comment = Comment(body=form.body.data,
                              blogpost=blogpost,
                              author=current_user,
                              notify=False, approved=True)
    else:
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(body=form.body.data,
                              blogpost=blogpost,
                              author_name=form.name.data,
                              author_email=form.email.data,
                              notify=form.notify.data, approved=False)
    if comment:
        db.session.add(comment)
        db.session.commit()
        if comment.approved:
            flash('Your comment has been published.')
        else:
            flash('Your comment will be published after it is reviewed by '
                  'the presenter.')
        return redirect(url_for('blog.getblogpost', id=blogpost.id) + '#top')
    comments = blogpost.comments.order_by(Comment.timestamp.asc()).all()
    headers = {}
    if current_user.is_authenticated():
        headers['X-XSS-Protection'] = '0'
    return render_template('blog/blogpost.html', ablogpost=blogpost, form=form,
                           comments=comments), 200, headers


@blog.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blogpost(id):
    ablogpost = BlogPost.query.get_or_404(id)
    if not current_user.is_admin and ablogpost.author != current_user:
        abort(403)
    form = BlogPostForm()
    if form.validate_on_submit():
        form.to_model(ablogpost)
        db.session.add(ablogpost)
        db.session.commit()
        flash('The blog post was updated successfully.')
        return render_template('blog/blogpost.html', id=ablogpost.id, ablogpost = ablogpost, form=form)
        #return redirect(url_for('.blogpost', id=ablogpost.id))
    form.from_model(ablogpost)
    return render_template('blog/edit_blogpost.html', form=form)



