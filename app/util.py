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
