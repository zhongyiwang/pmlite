from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required

from pmlite.models import RoleModel, PermissionModel, UserModel
from ..extensions import db
from ..decorators import permission_required

role_api = Blueprint("role", __name__, url_prefix="/role")


# 获取列表
@role_api.route('/')
def view():
    roles = db.session.execute(db.select(RoleModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(roles),
        'data': [item.json() for item in roles]
    }


# 添加
@role_api.post('/')
def add():
    data = request.get_json()
    role = RoleModel()
    role.update(data)
    try:
        role.save()
    except Exception as e:
        print(e)
        return {
            'code': -1,
            'msg': '新增数据失败'
        }
    return {
        'code': 0,
        'msg': '新增数据成功'
    }


# 修改
@role_api.put('/<int:_id>')
@permission_required('system_admin')
def edit(_id):
    data = request.get_json()
    role = db.get_or_404(RoleModel, _id)
    role.update(data)
    try:
        role.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


# 删除
@role_api.delete('/<int:_id>')
def delete(_id):
    role: RoleModel = db.get_or_404(RoleModel, _id)
    try:
        db.session.delete(role)
        db.session.commit()
    except Exception as e:
        return {
            'code': -1,
            'msg': '删除数据失败'
        }
    return {
        'code': 0,
        'msg': '删除数据成功'
    }


# 通过权限列表为角色添加权限
@role_api.put('/<int:role_id>/permissions')
@permission_required('system_admin')
def add_role_permissions(role_id):
    print(current_user)
    # 验证角色是否存在
    role = RoleModel.query.get(role_id)
    if not role:
        return {
            'code': -1,
            'msg': f'角色ID {role_id} 不存在'
        }
    permissions_ids = request.get_json()

    # 验证权限ID是否有效
    valid_permissions = PermissionModel.query.filter(PermissionModel.id.in_(permissions_ids)).all()
    valid_ids = [perm.id for perm in valid_permissions]

    invalid_ids = set(permissions_ids) - set(valid_ids)
    if invalid_ids:
        return {
            'code': -1,
            'msg': f'无效的权限ID： {list(invalid_ids)}'
        }

    # 添加权限
    success, message = role.add_permissions(valid_ids)
    if success:
        return {
            'code': 0,
            'msg': '权限添加成功'
        }
    else:
        return {
            'code': -1,
            'msg': '权限添加失败'
        }


# 通过权限列表为角色移除权限
@role_api.delete('/<int:role_id>/permissions')
@permission_required('system_admin')
def remove_role_permissions(role_id):
    # 验证角色是否存在
    role = RoleModel.query.get(role_id)
    if not role:
        return {
            'code': -1,
            'msg': f'角色ID {role_id} 不存在'
        }
    permissions_ids = request.get_json()

    # 验证权限ID是否有效
    valid_permissions = PermissionModel.query.filter(PermissionModel.id.in_(permissions_ids)).all()
    valid_ids = [perm.id for perm in valid_permissions]

    invalid_ids = set(permissions_ids) - set(valid_ids)
    if invalid_ids:
        return {
            'code': -1,
            'msg': f'无效的权限ID： {list(invalid_ids)}'
        }

    # 移除权限
    success, message = role.remove_permissions(valid_ids)
    if success:
        return {
            'code': 0,
            'msg': '权限移除成功'
        }
    else:
        return {
            'code': -1,
            'msg': '权限移除失败'
        }


# 通过用户列表为角色添加用户
@role_api.put('/<int:role_id>/users')
@permission_required('system_admin')
def add_role_users(role_id):
    # 验证角色是否存在
    role = RoleModel.query.get(role_id)
    if not role:
        return {
            'code': -1,
            'msg': f'角色ID {role_id} 不存在'
        }
    user_ids = request.get_json()

    # 验证用户ID是否有效
    valid_users = UserModel.query.filter(UserModel.id.in_(user_ids)).all()
    valid_ids = [perm.id for perm in valid_users]

    invalid_ids = set(user_ids) - set(valid_ids)
    if invalid_ids:
        return {
            'code': -1,
            'msg': f'无效的用户ID： {list(invalid_ids)}'
        }

    # 添加权限
    success, message = role.add_users(valid_ids)
    print(message)
    if success:
        return {
            'code': 0,
            'msg': '用户添加成功'
        }
    else:
        return {
            'code': -1,
            'msg': message[0] if message else '用户添加失败'
        }


# 通过用户列表为角色移除用户
@role_api.delete('/<int:role_id>/users')
@permission_required('system_admin')
def remove_role_users(role_id):
    # 验证角色是否存在
    role = RoleModel.query.get(role_id)
    if not role:
        return {
            'code': -1,
            'msg': f'角色ID {role_id} 不存在'
        }
    user_ids = request.get_json()

    # 验证用户ID是否有效
    valid_users = UserModel.query.filter(UserModel.id.in_(user_ids)).all()
    valid_ids = [perm.id for perm in valid_users]

    invalid_ids = set(user_ids) - set(valid_ids)
    if invalid_ids:
        return {
            'code': -1,
            'msg': f'无效的用户ID： {list(invalid_ids)}'
        }

    # 添加权限
    success, message = role.remove_users(valid_ids)
    print(message)
    if success:
        return {
            'code': 0,
            'msg': '用户移除成功'
        }
    else:
        return {
            'code': -1,
            'msg': message[0] if message else '用户移除失败'
        }
