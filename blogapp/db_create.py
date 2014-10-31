#!flask/bin/python
from migrate.versioning import *
from config import DevelopmentConfigTwo as dc
from blogapp import db
import os.path

SQLALCHEMY_DATABASE_URI = dc.SQLALCHEMY_DATABASE_URI
SQLALCHEMY_MIGRATE_REPO = dc.SQLALCHEMY_MIGRATE_REPO

with app.app_context():
    db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))