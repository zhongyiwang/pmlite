from flask import Blueprint, Flask

from .auth import auth_api
from .department import department_api
from .user import user_api
from .project import project_api
from .task import task_api
from .machine import machine_api
from .supplier import supplier_api
from .gantt import gantt_api
from .task_types import task_types_api
from .work_shape import work_shape_api
from .customer_industry import customer_industry_api
from .project_type import project_type_api
from .machining_process import machining_process_api
from .role import role_api
from .permission import permission_api


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
    apis.register_blueprint(task_types_api)
    apis.register_blueprint(work_shape_api)
    apis.register_blueprint(customer_industry_api)
    apis.register_blueprint(project_type_api)
    apis.register_blueprint(machining_process_api)
    apis.register_blueprint(role_api)
    apis.register_blueprint(permission_api)

    app.register_blueprint(apis)
