from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import Optional, Length, Required, URL, Email
from flask.ext.pagedown.fields import PageDownField


class ProfileForm(Form):
    name = StringField('Name', validators=[Optional(), Length(1, 64)])
    location = StringField('Location', validators=[Optional(), Length(1, 64)])
    bio = TextAreaField('Bio')
    submit = SubmitField('Submit')


class BlogPostForm(Form):
    title = StringField('Title', validators=[Required(), Length(1, 128)])
    description = TextAreaField('Description')
    slides = StringField('Slides Embed Code (450 pixels wide)')
    video = StringField('Video Embed Code (450 pixels wide)')
    venue = StringField('Venue',
                        validators=[Required(), Length(1, 128)])
    venue_url = StringField('Venue URL',
                            validators=[Optional(), Length(1, 128), URL()])
    date = DateField('Date')
    submit = SubmitField('Submit')

    def from_model(self, blogpost):
        self.title.data = blogpost.title
        self.description.data = blogpost.description
        self.slides.data = blogpost.slides
        self.video.data = blogpost.video
        self.venue.data = blogpost.venue
        self.venue_url.data = blogpost.venue_url
        self.date.data = blogpost.date

    def to_model(self, blogpost):
        blogpost.title = self.title.data
        blogpost.description = self.description.data
        blogpost.slides = self.slides.data
        blogpost.video = self.video.data
        blogpost.venue = self.venue.data
        blogpost.venue_url = self.venue_url.data
        blogpost.date = self.date.data


class PresenterCommentForm(Form):
    body = PageDownField('Comment', validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    name = StringField('Name', validators=[Required(), Length(1, 64)])
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    body = PageDownField('Comment', validators=[Required()])
    notify = BooleanField('Notify when new comments are posted', default=True)
    submit = SubmitField('Submit')

class SearchForm(Form):
    search = StringField('search', validators=[Required()])