from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required

from ..models import ProjectModel, TaskModel, ManHourModel
from ..extensions import db


project_api = Blueprint("project", __name__, url_prefix="/project")


# 获取项目列表
@project_api.route('/')
def project_view():
    projects = db.session.execute(db.select(ProjectModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(projects),
        'data': [project.json() for project in projects]
    }


# 获取项目列表，分页显示
@project_api.route('/pagination')
def project_view_pagination():
    status = request.args.get('status')
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=10)

    if status == "uncompleted":
        q = db.select(ProjectModel).where(ProjectModel.status != "已完成")
    else:
        q = db.select(ProjectModel)

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': pages.total,
        'data': [item.json() for item in pages.items]
    }




# 获取项目的任务列表
@project_api.get('/<int:pid>/tasks')
def project_tasks(pid):
    q = db.select(TaskModel).where(TaskModel.project_id == pid)
    task_list = db.session.execute(q).scalars().all()

    print(task_list)
    ret = []
    for child in task_list:
        child_data = child.json()
        # 查询并绑定实际工时
        child_data['actual_man_hours'] = db.session.query(db.func.sum(ManHourModel.man_hour)) \
            .filter(ManHourModel.task_id == child.id).scalar()
        if isinstance(child_data['actual_man_hours'], float):
            child_data['actual_man_hours'] = round(child_data['actual_man_hours'], 1)

        child_data["children"] = []
        if child.children:
            child_data["isParent"] = True
            for son in child.children:
                try:
                    task_list.remove(son)
                except:
                    pass
                finally:
                    son_data = son.json()
                    # 查询并绑定实际工时
                    son_data['actual_man_hours'] = db.session.query(db.func.sum(ManHourModel.man_hour)) \
                        .filter(ManHourModel.task_id == son.id).scalar()
                    if isinstance(son_data['actual_man_hours'], float):
                        son_data['actual_man_hours'] = round(son_data['actual_man_hours'], 1)

                    child_data['children'].append(son_data)
        ret.append(child_data)
    print(ret)
    return {
        "code": 0,
        "message": "数据请求成功！",
        "count": '',
        "data": ret
    }

# 添加
@project_api.post('/')
@jwt_required()
def project_add():
    data = request.get_json()
    project = ProjectModel()
    project.update(data)
    project.creator = current_user
    try:
        project.save()
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
@project_api.put('/<int:pid>')
def project_edit(pid):
    data = request.get_json()
    project = db.get_or_404(ProjectModel, pid)
    project.update(data)
    try:
        project.save()
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
@project_api.delete('/<int:pid>')
@jwt_required()
def project_delete(pid):
    project: ProjectModel = db.get_or_404(ProjectModel, pid)
    if project.creator == current_user:
        try:
            db.session.delete(project)
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
            'msg': '只能删除自己创建的项目'
        }