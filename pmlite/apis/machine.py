from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required

from pmlite.models import MachineTypeModel
from ..extensions import db


machine_api = Blueprint("machine", __name__, url_prefix="/machine")


# 获取用户列表
@machine_api.route('/')
def machine_view():
    machine_list = db.session.execute(db.select(MachineTypeModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(machine_list),
        'data': [item.json() for item in machine_list]
    }


# 添加
@machine_api.post('/')
def machine_add():
    data = request.get_json()
    machine = MachineTypeModel()
    machine.update(data)
    try:
        machine.save()
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


# 修改用户数据
@machine_api.put('/<int:uid>')
def machine_edit(uid):
    data = request.get_json()
    # user = StudentORM.query.get(uid)
    machine = db.get_or_404(MachineTypeModel, uid)
    machine.update(data)
    try:
        machine.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


# 删除用户
@machine_api.delete('/<int:uid>')
def user_delete(uid):
    user: UserModel = db.get_or_404(UserModel, uid)
    try:
        db.session.delete(user)
        # user.is_del = True
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


# 获取用户信息
@machine_api.get("/profile")
@jwt_required()
def user_profile():
    return {
        "code": 0,
        "msg": "获取个人数据成功！",
        "data": current_user.json()
    }
