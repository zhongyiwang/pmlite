from flask import jsonify
from functools import wraps
from flask import abort
# from .models import PermissionModel
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity, verify_jwt_in_request
from .models import UserModel, PermissionModel


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


# def admin_required(func):
#     return permission_required(Permission.ADMIN)(func)


def has_permission(permission):
    def decorator(func):
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = UserModel.query.get(user_id)
            if not user or not user.role or permission not in user.role.permissions.split(','):
                return jsonify({"msg": "没有权限"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator
