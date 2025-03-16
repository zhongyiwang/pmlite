from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required
# from pmlite.decorators import permission_required, admin_required
# from pmlite.models import Permission

gantt_bp = Blueprint('gantt', __name__, url_prefix="/gantt")


# 项目列表视图
@gantt_bp.route('/')
# @jwt_required()
# @permission_required(Permission.PROJECT)
def index():
    return render_template('gantt/gantt_index.html')

