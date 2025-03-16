from flask import Blueprint, render_template, request
from flask_jwt_extended import jwt_required
# from pmlite.decorators import permission_required, admin_required
# from pmlite.models import Permission

purchase_bp = Blueprint('purchase', __name__, url_prefix="/purchase")


# 项目列表视图
@purchase_bp.route('/')
# @jwt_required()
# @permission_required(Permission.PROJECT)
def index():
    return render_template('purchase/purchase_index.html')

