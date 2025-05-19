from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required

from pmlite.models import TaskTypeModel
from ..extensions import db


task_types_api = Blueprint("task_types", __name__, url_prefix="/task_types")


# 获取列表
@task_types_api.get('/')
def task_type_view():
    task_types = db.session.execute(db.select(TaskTypeModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(task_types),
        'data': [item.json() for item in task_types]
    }


# 添加
@task_types_api.post('/')
def task_type_add():
    data = request.get_json()
    task_type = TaskTypeModel()
    task_type.update(data)
    try:
        task_type.save()
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
@task_types_api.put('/<int:tyid>')
def task_type_edit(tyid):
    data = request.get_json()
    task_type = db.get_or_404(TaskTypeModel, tyid)
    task_type.update(data)
    try:
        task_type.save()
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
@task_types_api.delete('/<int:tyid>')
def task_type_delete(tyid):
    task_type: TaskTypeModel = db.get_or_404(TaskTypeModel, tyid)
    try:
        db.session.delete(task_type)
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
