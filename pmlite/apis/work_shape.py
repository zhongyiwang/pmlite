from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required

from pmlite.models import MachiningProcessModel, MachiningProcessStatusModel, WorkShapeModel, CustomerIndustryModel, ProjectTypeModel
from ..extensions import db


work_shape_api = Blueprint("work_shape", __name__, url_prefix="/work_shape")


# 获取列表
@work_shape_api.get('/')
def view():
    items = db.session.execute(db.select(WorkShapeModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(items),
        'data': [item.json() for item in items]
    }


# 添加
@work_shape_api.post('/')
def add():
    data = request.get_json()
    item = WorkShapeModel()
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
@work_shape_api.put('/<int:_id>')
def edit(_id):
    data = request.get_json()
    # print(data)
    # user = StudentORM.query.get(uid)
    item = db.get_or_404(WorkShapeModel, _id)
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
@work_shape_api.delete('/<int:_id>')
def delete(_id):
    item: WorkShapeModel = db.get_or_404(WorkShapeModel, _id)
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
@work_shape_api.get('/dropdown')
def dropdown():
    items = db.session.execute(db.select(WorkShapeModel)).scalars().all()
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
