from flask import Blueprint, render_template

machining_process_bp = Blueprint('machining_process', __name__, url_prefix='/machining_process')


# 部门列表视图
@machining_process_bp.route('/')
def index():
    return render_template("project/machining_process.html")
