from flask import Blueprint, render_template

project_bp = Blueprint('project', __name__, url_prefix="/project")


# 项目列表视图
@project_bp.route('/')
def index():
    print("111")
    # departments = DepartmentModel.query.all()
    return render_template('project/index.html')
