from flask import Blueprint, render_template, request

task_bp = Blueprint('task', __name__, url_prefix="/task")


# 项目列表视图
@task_bp.route('/')
def index():
    query = request.args.get('query')
    # departments = DepartmentModel.query.all()
    return render_template('task/task_index.html', query=query)


@task_bp.route('/man-hour')
def manHour():
    return render_template('task/task_manHour.html')
