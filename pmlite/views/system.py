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
