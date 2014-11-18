from flask.ext.mail import Message
from blogapp import mail
from flask import render_template, current_app
from threading import Thread
from config import ADMINS
from .decorators import async

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(current_app._get_current_object(), msg)


def follower_notification(followed, follower):
    send_email("[Internet Magic] %s is now following you!" % follower.username,
               ADMINS[0],
               [followed.email],
               render_template("follower_email.txt",
                               user=followed, follower=follower),
               render_template("follower_email.html",
                               user=followed, follower=follower))