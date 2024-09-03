from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required
from pmlite.decorators import permission_required, admin_required
from pmlite.models import Permission

task_bp = Blueprint('task', __name__, url_prefix="/task")


# 项目列表视图
@task_bp.route('/')
# @jwt_required()
# @permission_required(Permission.PROJECT)
def index():
    query = request.args.get('query')
    pid = request.args.get('pid')
    # departments = DepartmentModel.query.all()
    return render_template('task/task_index.html', query=query, pid=pid)


@task_bp.route('/man-hour')
def manHour():
    return render_template('task/task_manHour.html')
