from flask import jsonify
from functools import wraps
from flask import abort
from .models import Permission
from flask_jwt_extended import jwt_required, current_user


def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                # abort(403)
                # return {"msg": "没有访问权限", "code": -1}, 403
                return jsonify(msg="没有访问权限。")
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(func):
    return permission_required(Permission.ADMIN)(func)
