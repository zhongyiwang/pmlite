from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required
from pmlite.decorators import permission_required
# from pmlite.models import Permission

task_bp = Blueprint('task', __name__, url_prefix="/task")


# 项目列表视图
@task_bp.route('/')
# @jwt_required()
# @permission_required(Permission.PROJECT)
def index():
    print('args:', request.args, request.url)
    query = request.args.get('query')
    c_user = request.args.get('c_user')
    status = request.args.get('status')
    pid = request.args.get('pid')
    # departments = DepartmentModel.query.all()
    return render_template('task/task_index.html', query=query, pid=pid, c_user=c_user, status=status)


# 任务列表视图-new
@task_bp.route('/new')
def index2():
    status = request.args.get('status')  # 任务状态
    created = request.args.get('created')  # 我创建的
    directed = request.args.get('directed')  # 我负责的
    return render_template('task/task_index2.html', status=status, created=created, directed=directed)

@task_bp.route('/man-hour')
def manHour():
    return render_template('task/task_manHour.html')
