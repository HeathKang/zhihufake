#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from app import create_app,db
from app.models import Post,User,Role,Answer,Comment
from flask.ext.script import Manager,Shell,Server
from flask.ext.migrate import Migrate,MigrateCommand
import flask_whooshalchemyplus as whoolshalchemy


app = create_app(os.getenv('FLASKY_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)
whoolshalchemy.whoosh_index(app,Post)
whoolshalchemy.whoosh_index(app,User)
whoolshalchemy.whoosh_index(app,Answer)


def make_shell_context():
    return dict(app=app,db=db,Post=Post,User=User,Role=Role,Answer=Answer,Comment=Comment)
manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)
manager.add_command('runserver',Server(threaded=True))


@manager.command
def test():
    '''测试开始'''
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()