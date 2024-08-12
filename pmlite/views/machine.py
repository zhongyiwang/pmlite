from flask import Blueprint, render_template, request

machine_bp = Blueprint('machine', __name__, url_prefix="/machine")


# 项目列表视图
@machine_bp.route('/')
def index():
    return render_template('machine/index.html')
