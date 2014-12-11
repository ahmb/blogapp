from . import db, login_manager
from datetime import datetime
import hashlib
from markdown import markdown
import bleach
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import request, current_app
from flask.ext.login import UserMixin
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base()





followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),
                      nullable=False, unique=True, index=True)
    username = db.Column(db.String(64),
                         nullable=False, unique=True, index=True)
    is_admin = db.Column(db.Boolean)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    bio = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime)
    avatar_hash = db.Column(db.String(32))
    blogpost = db.relationship('BlogPost', lazy='dynamic', backref='author')
    comments = db.relationship('Comment', lazy='dynamic', backref='author')
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')
    '''
    comment for ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    'User' is the right side entity that is in this relationship (the left side entity is the parent class). Since we are defining a self-referential relationship we use the same class on both sides.
    secondary indicates the association table that is used for this relationship.
    primaryjoin indicates the condition that links the left side entity (the follower user) with the association table. Note that because the followers table is not a model there is a slightly odd syntax required to get to the field name.
    secondaryjoin indicates the condition that links the right side entity (the followed user) with the association table.
    backref defines how this relationship will be accessed from the right side entity. We said that for a given user the query named followed returns all the right side users that have the target user on the left side. The back reference will be called followers and will return all the left side users that are linked to the target user in the right side. The additional lazy argument indicates the execution mode for this query. A mode of dynamic sets up the query to not run until specifically requested. This is useful for performance reasons, and also because we will be able to take this query and modify it before it executes. More about this later.
    lazy is similar to the parameter of the same name in the backref, but this one applies to the regular query instead of the back reference.
    '''

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    #property getter
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or \
               hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def for_moderation(self, admin=False):
        if admin and self.is_admin:
            return Comment.for_moderation()
        return Comment.query.join(BlogPost, Comment.blogpost_id == BlogPost.id).\
            filter(BlogPost.author == self).filter(Comment.approved == False)

    def get_api_token(self, expiration=300):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'user': self.id}).decode('utf-8')

    @staticmethod
    def validate_api_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        id = data.get('user')
        if id:
            return User.query.get(id)
        return None

    @staticmethod
    def register(username, password):
        user = User(username=username)
        user.password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return BlogPost.query.join(followers, (followers.c.followed_id == BlogPost.user_id)).filter(followers.c.follower_id == self.id).order_by(BlogPost.timestamp.desc())

    def follows_oneself(self):
        if self.is_following(self):
            pass
        else:
           self.follow(self)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class BlogPost(db.Model):
    __tablename__ = 'blogposts'
    __searchable__ = ['title', 'description']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    slides = db.Column(db.Text())
    video = db.Column(db.Text ())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    venue = db.Column(db.String(128))
    venue_url = db.Column(db.String(128))
    date = db.Column(db.DateTime())
    comments = db.relationship('Comment', lazy='dynamic', backref='blogpost')

    def __repr__(self):
        return '<Blog Post content is: %r>' % self.description

    def approved_comments(self, count=False):
        if count is not False:
            return self.comments.filter_by(approved=True).count()
        return self.comments.filter_by(approved=True)



class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author_name = db.Column(db.String(64))
    author_email = db.Column(db.String(64))
    notify = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)
    blogpost_id = db.Column(db.Integer, db.ForeignKey('blogposts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    @staticmethod
    def for_moderation():
        return Comment.query.filter(Comment.approved == False)

db.event.listen(Comment.body, 'set', Comment.on_changed_body)


