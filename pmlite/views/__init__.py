from flask import Flask

from .index import index_bp
from .department import department_bp
from .user import user_bp
from .project import project_bp
from .task import task_bp
from .machine import machine_bp


def register_views(app: Flask):
    app.register_blueprint(index_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(machine_bp)

    app.jinja_env.auto_reload = True

