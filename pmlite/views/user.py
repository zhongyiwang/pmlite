from flask import Blueprint, render_template
from pmlite.models import DepartmentModel
from flask_jwt_extended import jwt_required

user_bp = Blueprint('user', __name__, url_prefix="/user")


# 用户列表视图
@user_bp.route('/')
def index():
    departments = DepartmentModel.query.all()
    return render_template('user/user_index.html')


# 用户登录视图
@user_bp.get('/login')
def login():
    return render_template('user/login.html')


# 个人信息
@user_bp.route('/profile')
def profile():
    return render_template('user/profile.html')