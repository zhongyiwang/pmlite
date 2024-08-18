from datetime import datetime
from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required

from ..models import TaskModel, TaskTypeModel, ManHourModel
from ..extensions import db

task_api = Blueprint("task", __name__, url_prefix="/task")


# 获取任务列表
@task_api.route('/')
def task_view():
    status = request.args.get('status')
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=10)
    if status == "uncompleted":
        q = db.select(TaskModel).where(TaskModel.status != "已完成")
    else:
        q = db.select(TaskModel)

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': pages.total,
        'data': [item.json() for item in pages.items]
    }


# 获取任务列表，以树状表格显示
@task_api.get("/treetable")
def task_list_as_treetable():
    q = db.select(TaskModel)
    q = q.where(TaskModel.parent_id == 0)
    task_list = db.session.execute(q).scalars()
    #print(task_list)
    ret = []
    for child in task_list:
        print(child.json())
        child_data = child.json()
        child_data["children"] = []
        if child.children:
            child_data["isParent"] = True
        for son in child.children:
            son_data = son.json()
            child_data['children'].append(son_data)
        ret.append(child_data)
    print(ret)
    return {
        "code": 0,
        "message": "数据请求成功！",
        "data": ret
    }


# 获取任务类型列表
@task_api.route('/types')
def task_type_list():
    task_types = db.session.execute(db.select(TaskTypeModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': "",
        'data': [item.json() for item in task_types]
    }


# 添加
@task_api.post('/')
@jwt_required()
def task_add():
    data = request.get_json()
    task = TaskModel()
    task.update(data)
    task.creator_id = current_user.id
    try:
        task.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '新增数据失败'
        }
    return {
        'code': 0,
        'msg': '新增数据成功'
    }


# 修改
@task_api.put('/<int:tid>')
def task_edit(tid):
    data = request.get_json()
    task = db.get_or_404(TaskModel, tid)
    task.update(data)
    try:
        task.save()
    except Exception as e:
        print(e)
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


# 删除
@task_api.delete('/<int:tid>')
@jwt_required()
def task_delete(tid):
    task: TaskModel = db.get_or_404(TaskModel, tid)
    if task.creator.name == current_user.name:
        try:
            pass
            db.session.delete(task)
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
    else:
        return{
            'code': -1,
            'msg': "只能删除自己创建的任务。"
        }


# 获取某任务工时列表
@task_api.get('/<int:tid>/man-hour')
def man_hour_list(tid):
    q = db.select(ManHourModel).where(ManHourModel.task_id == tid)
    MHlist = db.session.execute(q).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': "",
        'data': [item.json() for item in MHlist]
    }


# 添加工时
@task_api.post('/<int:tid>/man-hour')
@jwt_required()
def man_hour_add(tid):
    data = request.get_json()
    man_hour = ManHourModel()
    man_hour.update(data)
    man_hour.user_id = current_user.id
    print(man_hour)
    try:
        man_hour.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '新增数据失败'
        }
    return {
        'code': 0,
        'msg': '新增数据成功'
    }


# 修改工时
@task_api.put('/<int:tid>/man-hour/<int:mid>')
def man_hour_edit(tid, mid):
    data = request.get_json()
    man_hour = db.get_or_404(ManHourModel, mid)
    man_hour.update(data)
    try:
        man_hour.save()
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
@task_api.delete('/<int:tid>/man-hour/<int:mid>')
@jwt_required()
def man_hour_delete(tid, mid):
    man_hour: ManHourModel = db.get_or_404(ManHourModel, mid)
    try:
        pass
        db.session.delete(man_hour)
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
