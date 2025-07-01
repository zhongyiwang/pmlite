from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required

from pmlite.models import PermissionModel
from ..extensions import db


permission_api = Blueprint("permission", __name__, url_prefix="/permission")


# 获取列表
@permission_api.route('/')
def view():
    items = db.session.execute(db.select(PermissionModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(items),
        'data': [item.json() for item in items]
    }


# 添加
@permission_api.post('/')
def add():
    data = request.get_json()
    item = PermissionModel()
    item.update(data)
    try:
        item.save()
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
@permission_api.put('/<int:_id>')
def edit(_id):
    data = request.get_json()
    item = db.get_or_404(PermissionModel, _id)
    item.update(data)
    try:
        item.save()
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
@permission_api.delete('/<int:_id>')
def delete(_id):
    item: PermissionModel = db.get_or_404(PermissionModel, _id)
    try:
        db.session.delete(item)
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


# 返回穿梭框格式data数据
@permission_api.get('/transfer')
def transfer():
    items = db.session.execute(db.select(PermissionModel)).scalars().all()
    ret = []
    for item in items:
        data = {
            "value": item.id,
            "title": item.desc
        }
        ret.append(data)
    return ret
