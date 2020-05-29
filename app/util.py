import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from threading import Thread
from flask import current_app, render_template, flash
from flask_mail import Message
from app import mail


def _send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to: list, subject: str, template: str, **kwargs):
    msg = Message(current_app.config['MAIL_SUBJECT_PREFIX'] + subject,
        sender=current_app.config['MAIL_SENDER'], recipients=to)
    msg.body = render_template(f'{ template }.txt', **kwargs)
    msg.html = render_template(f'{ template }.html', **kwargs)

    thr = Thread(target=_send_async_email, args=[current_app._get_current_object(), msg])
    thr.start()
    return thr


def flash_form_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error)


def mail_logger(app):
    credentials = None
    secure = None
    
    if app.config['MAIL_USERNAME']:
        credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        if app.config['MAIL_USE_TLS']:
            secure =()
    
    mail_handler = SMTPHandler(
        mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        fromaddr=app.config['MAIL_SENDER'],
        toaddrs=[app.config['ADMIN']],
        subject=app.config['MAIL_SUBJECT_PREFIX'] + ' Application Error',
        credentials=credentials, secure=secure)
    
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


def file_logger(app):
    log_dir = os.path.join('tmp', 'logs')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    
    file_handler = RotatingFileHandler(os.path.join(log_dir, '.log'), maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('App startup')
        