#!/usr/bin/env python
import os
from blogapp import db, create_app
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from blogapp.models import BlogPost
from config import *

#Create the app from the configuration outlined in config.py; the default which is being used is developmental
#commenting out this one because there is a version below
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

#with app.app_context():
#   db.create_all()

#SET UP LOGGING HERE

import logging
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler('tmp/internetmagic.log', 'a', 1 * 1024 * 1024, 10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.setLevel(logging.INFO)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.info('microblog startup')

if not app.debug:
    import logging
    import logging.handlers
    credentials = None

    if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
        credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

    #To use gmail you have to extend logging.handlers.SMTPHandler class and override SMTPHandler.emit() method.
    class TlsSMTPHandler(logging.handlers.SMTPHandler):
        def emit(self, record):
            """
            Emit a record.

            Format the record and send it to the specified addressees.
            """
            try:
                import smtplib
                import string # for tls add this line
                try:
                    from email.utils import formatdate
                except ImportError:
                    #formatdate = self.date_time
                    pass
                port = app.config['MAIL_PORT']
                if not port:
                    port = smtplib.SMTP_PORT
                smtp = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])

                msg = self.format(record)
                msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                                self.fromaddr,
                                string.join(self.toaddrs, ","),
                                self.getSubject(record),
                                formatdate(), msg)
                if self.username:
                    smtp.ehlo() # for tls add this line
                    smtp.starttls() # for tls add this line
                    smtp.ehlo() # for tls add this line
                    smtp.login(self.username, self.password)
                smtp.sendmail(self.fromaddr, self.toaddrs, msg)
                smtp.quit()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)

    logger = logging.getLogger()
    #    def __init__(self, mailhost, fromaddr, toaddrs, subject, \
    #            credentials=None, secure=None):
    gmail_handler = TlsSMTPHandler((app.config['MAIL_SERVER'], app.config['MAIL_PORT']), 'no-reply@' + app.config['MAIL_SERVER'], app.config['ADMINS'], 'Internet Magic blog failure', \
                                   credentials)

    gmail_handler.setLevel(logging.ERROR)

    app.logger.addHandler(gmail_handler)



migrate = Migrate(app, db)

manager = Manager(app)
import sys

#Enable Whoosh-Alchemy if python version is lower than 3

if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True

if enable_search is True:
    import flask.ext.whooshalchemy as whooshalchemy
    whooshalchemy.whoosh_index(app, BlogPost)

@manager.command
def adduser(email, username, admin=False):
    """Register a new user."""
    from blogapp.models import User
    from getpass import getpass
    password = getpass()
    password2 = getpass(prompt='Confirm: ')
    if password != password2:
        import sys
        sys.exit('Error: passwords do not match.')
    db.create_all()
    user = User(email=email, username=username, password=password,
                is_admin=admin)
    db.session.add(user)
    db.session.commit()
    print('User {0} was registered successfully.'.format(username))

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':

    #manager.run()
    app.run()
