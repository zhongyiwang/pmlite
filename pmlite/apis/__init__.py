from flask import Blueprint, Flask

from .auth import auth_api
from .department import department_api
from .user import user_api
from .project import project_api
from .task import task_api
from .machine import machine_api
from .supplier import supplier_api
from .gantt import gantt_api


def register_apis(app: Flask):
    apis = Blueprint("api", __name__, url_prefix="/api/v1")

    apis.register_blueprint(auth_api)
    apis.register_blueprint(department_api)
    apis.register_blueprint(user_api)
    apis.register_blueprint(project_api)
    apis.register_blueprint(task_api)
    apis.register_blueprint(machine_api)
    apis.register_blueprint(supplier_api)
    apis.register_blueprint(gantt_api)

    app.register_blueprint(apis)
