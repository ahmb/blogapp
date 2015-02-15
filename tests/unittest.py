#!flask/bin/python
import os
import unittest

from config import basedir
from blogapp import db
from blogapp.models import User
from manage import app


import coverage

"""#pip install fake-factory
from faker import Factory

#----------------------------------------------------------------------
def create_fake_stuff(fake):
    """"""
    stuff = ["email", "bs", "address",
             "city", "state",
             "paragraph"]
    for item in stuff:
        print "%s = %s" % (item, getattr(fake, item)())

if __name__ == "__main__":
    fake = Factory.create()
    create_fake_stuff(fake)"""

COV = coverage.coverage(branch=True, include='blogapp/*')
COV.start

#import unit tests from other tests folder files and then compile into a suite
suite = unittest.TestLoader().discover(start_dir='.', pattern='test*.py')

unittest.TextTestRunner(verbosity=2).run(suite)

COV.stop
COV.report
