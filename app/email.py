#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')


from threading import Thread
from flask import current_app,render_template
from flask.ext.mail import Message
from . import mail





def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to,subject,template,**kwargs):

    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + '' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])

    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    msg.charset = "UTF-8"
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr