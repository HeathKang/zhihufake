#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from app import create_app,db
from app.models import Post,User,Role
from flask.ext.script import Manager,Shell
from flask.ext.migrate import Migrate,MigrateCommand

app = create_app(os.getenv('FLASKY_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)


def make_shell_context():
    return dict(app=app,db=db,Post=Post,User=User,Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)


if __name__ == '__main__':
    manager.run()