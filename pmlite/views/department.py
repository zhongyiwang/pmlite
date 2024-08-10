from flask import Blueprint, render_template

department_bp = Blueprint('department', __name__, url_prefix='/department')


# 部门列表视图
@department_bp.route('/')
def index():
    return render_template("department/index.html")