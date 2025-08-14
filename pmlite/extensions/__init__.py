from flask import Flask

from .init_db import db, migrate
from .init_jwt import jwt
from .init_script import register_script
from .init_mail import mail


def register_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    register_script(app)
