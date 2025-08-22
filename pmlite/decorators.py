from flask import jsonify
from functools import wraps
from sqlalchemy import select
from flask import abort
# from .models import PermissionModel
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity, verify_jwt_in_request
from .models import UserModel, PermissionModel
from .extensions import db


def permission_required(permission_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()  # 验证JWT
            if not current_user or not current_user.role:
                return jsonify({"msg": "没有用户或用户为注册角色。"}), 403
            # 检查用户角色是否拥有该权限
            permission = PermissionModel.query.filter_by(name=permission_name).first()
            if not permission or permission not in current_user.role.permissions:
                return jsonify({"msg": "用户没有权限。"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 视图函数内部检查权限
def has_permission(permission_name):
    if not current_user or not current_user.role:
        return False

    stmt = select(PermissionModel).where(PermissionModel.name == permission_name)
    permission = db.session.execute(stmt).scalar_one_or_none()

    return permission is not None and permission in current_user.role.permissions
