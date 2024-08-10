from flask import Blueprint, render_template, request

task_bp = Blueprint('task', __name__, url_prefix="/task")


# 项目列表视图
@task_bp.route('/')
def index():
    status = request.args.get('status')
    # departments = DepartmentModel.query.all()
    return render_template('task/task_index.html', status=status)
