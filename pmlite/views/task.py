from flask import Blueprint, render_template, request

task_bp = Blueprint('task', __name__, url_prefix="/task")


# 项目列表视图
@task_bp.route('/')
def index():
    print(request.args)
    query = request.args.get('query')
    print("view")
    print(query)
    # departments = DepartmentModel.query.all()
    return render_template('task/task_index.html', query=query)
