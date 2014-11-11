#!/usr/bin/env python
import os
from blogapp import db, create_app
from flask.ext.script import Manager
from blogapp.models import User
from flask.ext.migrate import Migrate, MigrateCommand
from config import config
from config import MAIL_PORT, MAIL_PASSWORD, MAIL_SERVER, MAIL_USE_SSL, MAIL_USE_TLS, MAIL_USERNAME, ADMINS


#Create the app from the configuration outlined in config.py; the default which is being used is developmental
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

#SET UP LOGGING HERE
if not app.debug:
    import logging
    import logging.handlers

    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)

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
                port = MAIL_PORT
                if not port:
                    port = smtplib.SMTP_PORT
                smtp = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)

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
    gmail_handler = TlsSMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'Microblog failure', \
                                   credentials)

    gmail_handler.setLevel(logging.ERROR)

    app.logger.addHandler(gmail_handler)



migrate = Migrate(app, db)

manager = Manager(app)

@manager.command
def adduser(email, username, admin=False):
    """Register a new user."""
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