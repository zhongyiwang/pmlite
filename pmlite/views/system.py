from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required
# from pmlite.decorators import permission_required, admin_required
# from pmlite.models import Permission

system_bp = Blueprint('system', __name__, url_prefix="/system")


# 项目列表视图
@system_bp.route('/supplier')
# @jwt_required()
# @permission_required(Permission.PROJECT)
def supplier():
    return render_template('system/supplier_index.html')


# 任务类型视图
@system_bp.route('/task_type')
def task_type():
    return render_template('task/task_type.html')


# 工件形状列表视图
@system_bp.route('/work_shape')
def work_shape():
    return render_template('system/work_shape_index.html')


# 客户行业列表视图
@system_bp.route('/customer_industry')
def customer_industry():
    return render_template('system/customer_industry_index.html')


# 项目类型列表视图
@system_bp.route('/project_type')
def project_type():
    return render_template('system/project_type_index.html')


# 用户角色管理
@system_bp.route('/user_role')
def user_role():
    return render_template('system/role_index.html')


# 权限管理
@system_bp.route('/role_permission')
def role_permission():
    return render_template('system/role_permission.html')
