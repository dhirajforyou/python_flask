import logging
from threading import Thread

from flask import current_app as app, render_template, copy_current_request_context
from flask_mail import Message

from . import mail

logger = logging.getLogger(__name__)


def create_message(to, subject, template, **kwargs):
    logger.info("Sending to %s" % to)
    recipients = to if isinstance(to, list) else [to]
    msg = Message(app.config.get("MAIL_SUBJECT_PREFIX") + subject,
                  sender=app.config["MAIL_SENDER"], recipients=recipients)
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    return msg


def send_email(to, subject, template, **kwargs):
    # Send mail in sync
    message = create_message(to, subject, template, **kwargs)
    logger.debug("Prepared mail message")
    mail.send(message)
    logger.debug("Sent mail")


def send_async_mail(to, subject, template, **kwargs):
    # send mail in async
    message = create_message(to, subject, template, **kwargs)
    logger.debug("Prepared mail message")

    # copy_current_request_context will add app context
    @copy_current_request_context
    def send_message(message):
        mail.send(message)
        logger.debug("Mail sent")

    sender = Thread(name='mail_sender', target=send_message, args=(message,))
    sender.start()
    logger.debug("Thread started")
