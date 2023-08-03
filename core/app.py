from flask import Flask, redirect, url_for
from flask_minify import Minify
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_babel import Babel
import logging

application = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)

application.config.from_pyfile("config.py")

bcrypt = Bcrypt()
bcrypt.init_app(application)

mail = Mail()
mail.init_app(application)

babel = Babel()
babel.init_app(application)

Minify(application)

FILES_DIR = application.config["UPLOAD_FILES_DIR"]

markdown_extensions = [
    "markdown.extensions.abbr",
    "markdown.extensions.admonition",
    "markdown.extensions.attr_list",
    "markdown.extensions.codehilite",
    "markdown.extensions.def_list",
    "markdown.extensions.extra",
    "markdown.extensions.fenced_code",
    "markdown.extensions.footnotes",
    "markdown.extensions.legacy_attrs",
    "markdown.extensions.legacy_em",
    "markdown.extensions.meta",
    "markdown.extensions.nl2br",
    "markdown.extensions.sane_lists",
    "markdown.extensions.tables",
    "markdown.extensions.toc",
]


def send_mail(subject, *args, **kwargs):
    """Sends mail"""
    try:
        message = Message(subject, *args, **kwargs)
        mail.send(message)
    except Exception as e:
        logging.exception(e)


@application.template_global()
def str_(element):
    return str(element)


@application.route("/", methods=["GET", "POST"])
def home():
    return redirect(url_for("notes1.index"))
