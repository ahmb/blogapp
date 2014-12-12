from flask import render_template, flash, redirect, url_for, abort,\
    request, current_app, g, jsonify
from .. import db
from flask.ext.login import login_required, current_user
from . import blog
from blogapp.models import User, BlogPost, Comment
from .forms import ProfileForm, BlogPostForm, CommentForm, PresenterCommentForm, SearchForm
from datetime import datetime
from blogapp.emails import follower_notification
from config import LANGUAGES
from flask.ext.sqlalchemy import get_debug_queries

# authentication token route
from ..auth import authx
@blog.route('/get-auth-token')
@authx.login_required
def get_auth_token():
    return jsonify({'token': g.user.get_api_token()})

@blog.before_request
def before_request():
    g.user = current_user
    g.search_form = SearchForm()
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@blog.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['DATABASE_QUERY_TIMEOUT']:
            current_app._get_current_object().logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))
    return response

@blog.route('/search', methods=['POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('blog.index'))
    return redirect(url_for('blog.search_results', query=g.search_form.search.data))

@blog.route('/search_results/<query>')
def search_results(query):
    results = BlogPost.query.whoosh_search(query, current_app.config['MAX_SEARCH_RESULTS']).all()
    return render_template('blog/search_results.html',
                           query=query,
                           blogposts=results)

@blog.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = BlogPost.query.order_by(BlogPost.date.desc()).paginate(
        page, per_page=current_app.config['TALKS_PER_PAGE'],
        error_out=False)
    blogpost_list = pagination.items
    return render_template('blog/index.html', blogposts=blogpost_list,
                           pagination=pagination)

@blog.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.blogpost.order_by(BlogPost.date.desc()).paginate(
        page, per_page=current_app.config['TALKS_PER_PAGE'],
        error_out=False)


    blogpost_list = pagination.items
    return render_template('blog/user.html', user=user, blogposts=blogpost_list,
                           pagination=pagination)


@blog.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('blog.index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('blog.user', username=username))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + username + '.')
        return redirect(url_for('blog.user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + username + '!')
    #Everytime the below function is used to send an email via gmail SMTP servers , the following error is recieved:
    follower_notification(user, g.user)
    '''socket.error
    error: [Errno 10061] No connection could be made because the target machine actively refused it'''
    return redirect(url_for('blog.user', username=username))

@blog.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('blog.index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('blog.user', username=username))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + username + '.')
        return redirect(url_for('blog.user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + username + '.')
    return redirect(url_for('blog.user', username=username))

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
    if blogpost.author == current_user or \
            (current_user.is_authenticated() and current_user.is_admin):
        comments_query = blogpost.comments
    else:
        comments_query = blogpost.approved_comments()

    page = request.args.get('page', 1, type=int)
    pagination = comments_query.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)

    comments = pagination.items
    headers = {}

    if current_user.is_authenticated():
        headers['X-XSS-Protection'] = '0'
    return render_template('blog/blogpost.html', ablogpost=blogpost, form=form,
                           comments=comments, pagination=pagination),\
           200, headers


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
        return redirect(url_for('blog.getblogpost', id=ablogpost.id))
        #return redirect(url_for('.blogpost', id=ablogpost.id))
    form.from_model(ablogpost)
    return render_template('blog/edit_blogpost.html', form=form)

@blog.route('/moderate')
@login_required
def moderate():
    comments = current_user.for_moderation().order_by(Comment.timestamp.asc())
    return render_template('blog/moderate.html', comments=comments)


@blog.route('/moderate-admin')
@login_required
def moderate_admin():
    if not current_user.is_admin:
        abort(403)
    comments = Comment.for_moderation().order_by(Comment.timestamp.asc())
    return render_template('blog/moderate.html', comments=comments)

