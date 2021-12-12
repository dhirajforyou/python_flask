from flask import render_template, jsonify
import logging

from werkzeug.exceptions import HTTPException

from . import main

logger = logging.getLogger(__name__)


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@main.errorhandler(Exception)
def handle_error(e):
    logger.debug("Exception %s" % e)
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

