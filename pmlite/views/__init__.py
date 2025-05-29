from flask import Flask

from .index import index_bp
from .department import department_bp
from .user import user_bp
from .project import project_bp
from .task import task_bp
from .machine import machine_bp
from .purchase import purchase_bp
from .system import system_bp
from .gantt import gantt_bp
from .machining_process import machining_process_bp


def register_views(app: Flask):
    app.register_blueprint(index_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(machine_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(gantt_bp)
    app.register_blueprint(machining_process_bp)

    app.jinja_env.auto_reload = True

