from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required

from pmlite.models import ProjectTypeModel
from ..extensions import db


project_type_api = Blueprint("project_type", __name__, url_prefix="/project_type")


# 获取列表
@project_type_api.route('/')
def listview():
    items = db.session.execute(db.select(ProjectTypeModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(items),
        'data': [item.json() for item in items]
    }


# 添加
@project_type_api.post('/')
def mp_add():
    data = request.get_json()
    item = ProjectTypeModel()
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
@project_type_api.put('/<int:_id>')
def edit(_id):
    data = request.get_json()
    # print(data)
    # user = StudentORM.query.get(uid)
    item = db.get_or_404(ProjectTypeModel, _id)
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
@project_type_api.delete('/<int:_id>')
def delete(_id):
    item: ProjectTypeModel = db.get_or_404(ProjectTypeModel, _id)
    try:
        db.session.delete(item)
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


# 返回drowpdown的data数据
@project_type_api.get('/dropdown')
def dropdown():
    items = db.session.execute(db.select(ProjectTypeModel)).scalars().all()
    ret = []
    _id = 100
    for item in items:
        title = item.name
        data = {
            "title": title,
            "id": _id
        }
        ret.append(data)
        _id += 1
    return ret
