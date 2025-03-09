from flask import Blueprint, render_template, request

project_bp = Blueprint('project', __name__, url_prefix="/project")


# 项目列表视图
@project_bp.route('/')
def index():
    status = request.args.get('status')
    return render_template('project/index.html', status=status)


@project_bp.route('/new')
def index2():
    status = request.args.get('status')
    return render_template('project/project_index2.html', status=status)


# 自动化项目列表视图
@project_bp.route('/automation')
def automation():
    return render_template('project/project_automation.html')


# 项目详细视图
@project_bp.route('/<int:pid>')
def main(pid):
    return render_template('project/project_index.html')


# 项目计划版本管理
@project_bp.route('/plan_version')
def plan_version():
    return render_template('project/project_plan_version.html')


# 项目计划签章管理
@project_bp.route('/plan_signature')
def plan_signature():
    return render_template('project/project_plan_signature.html')


# 项目节点
@project_bp.route('/node_title')
def node_title():
    return render_template('project/project_node_title.html')