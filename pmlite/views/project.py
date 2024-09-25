from flask import Blueprint, render_template, request

project_bp = Blueprint('project', __name__, url_prefix="/project")


# 项目列表视图
@project_bp.route('/')
def index():
    status = request.args.get('status')
    return render_template('project/index.html', status=status)
