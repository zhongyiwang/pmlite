from datetime import datetime
from flask import Blueprint, request
from sqlalchemy import desc
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy.event import listen
from flask_jwt_extended import current_user, jwt_required

from ..models import TaskModel, TaskTypeModel, ManHourModel, DepartmentModel, UserModel
from ..extensions import db
from pmlite.decorators import permission_required, has_permission

task_api = Blueprint("task", __name__, url_prefix="/task")


# 获取任务列表
@task_api.route('/')
@jwt_required()
def task_view():
    query = request.args.get('query')
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=10)
    if query == "uncompleted":
        q = db.select(TaskModel).where(TaskModel.status != "已完成")
    elif query == "mine":
        q = db.select(TaskModel).where(TaskModel.owner == current_user)
    else:
        q = db.select(TaskModel)

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    # 将返回的任务数据中加入实际工时
    ret = []
    for item in pages.items:
        item_json = item.json()
        item_json['actual_man_hours'] = db.session.query(db.func.sum(ManHourModel.man_hour)) \
            .filter(ManHourModel.task_id == item.id).scalar()
        ret.append(item_json)

    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': pages.total,
        'data': ret
    }


# 获取任务列表-new
@task_api.route('/new')
@jwt_required()
def task_view2():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=10)
    status = request.args.get('status')
    created = request.args.get('created')
    directed = request.args.get('directed')
    date_start = request.args.get('start')
    date_end = request.args.get('end')
    user_id = request.args.get('user_id')
    department_id = request.args.get('department_id')
    if department_id:
        user_id = None

    print('api_url', request.url)
    q = db.select(TaskModel).order_by(desc(TaskModel.id))
    if status == 'uncompleted':
        q = q.where(TaskModel.status != '已完成')
    if created:  # 我创建的
        q = q.where(TaskModel.creator == current_user)
    if directed:  # 我负责的
        q = q.where(TaskModel.owner == current_user)
    if user_id:
        q = q.where(TaskModel.owner_id == user_id)
    if date_start:
        q = q.where(TaskModel.planned_start_date >= date_start)
    if date_end:
        q = q.where(TaskModel.planned_end_date <= date_end)

    if department_id:
        user_list = []
        users = db.session.execute(db.select(UserModel).where(UserModel.department_id == department_id)).scalars().all()
        for user in users:
            user_list.append(user.id)
        q = q.where(TaskModel.owner_id.in_(user_list))

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    ret = []
    for item in pages.items:
        item_json = item.json()
        if item.parent_id:
            print(item.title, item.parent.title)
            item_json['title'] = item_json['title'] + ' → ' + item.parent.title
        ret.append(item_json)

    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': pages.total,
        'data': ret
    }


# 获取任务列表-new
@task_api.route('/new2')
@jwt_required()
def task_view3():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=10)
    status = request.args.get('status')
    created = request.args.get('created')
    directed = request.args.get('directed')
    date_start = request.args.get('start')
    date_end = request.args.get('end')
    user_id = request.args.get('user_id')
    department_id = request.args.get('department_id')
    if department_id:
        user_id = None

    print('api_url', request.url)
    q = db.select(TaskModel).order_by(desc(TaskModel.id))
    if status == 'uncompleted':
        q = q.where(TaskModel.status != '已完成')
    if created:  # 我创建的
        q = q.where(TaskModel.creator == current_user)
    if directed:  # 我负责的
        q = q.where(TaskModel.owner == current_user)
    if user_id:
        q = q.where(TaskModel.owner_id == user_id)
    if date_start:
        q = q.where(TaskModel.planned_start_date >= date_start)
    if date_end:
        q = q.where(TaskModel.planned_end_date <= date_end)

    if department_id:
        user_list = []
        users = db.session.execute(db.select(UserModel).where(UserModel.department_id == department_id)).scalars().all()
        for user in users:
            user_list.append(user.id)
        q = q.where(TaskModel.owner_id.in_(user_list))

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    ret = []
    for item in pages.items:
        item_json = item.json()
        if item.parent_id:
            print(item.title, item.parent.title)
            item_json['title'] = item_json['title'] + ' → ' + item.parent.title
        ret.append(item_json)

    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': pages.total,
        'data': ret
    }

# 获取某任务工时列表
@task_api.get('/<int:tid>/subTasks')
def sub_task_list(tid):
    task: TaskModel = db.get_or_404(TaskModel, tid)
    subTasks = task.children

    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(subTasks),
        'data': [item.json() for item in subTasks]
    }



# 获取工时列表
@task_api.route('/man-hour')
@jwt_required()
def manHour_view():
    print('url:',request.url)
    date_start = request.args.get('start')
    date_end = request.args.get('end')
    user_id = request.args.get('user_id')
    department_id = request.args.get('department_id')

    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=30)
    q = db.select(ManHourModel).order_by(desc(ManHourModel.work_date))
    if user_id:
        q = q.where(ManHourModel.user_id == user_id)
        department_id = ""
    if date_start:
        q = q.where(ManHourModel.work_date >= date_start)
    if date_end:
        q = q.where(ManHourModel.work_date <= date_end)
    if department_id:
        user_list = []
        users = db.session.execute(db.select(UserModel).where(UserModel.department_id == department_id)).scalars().all()
        for user in users:
            user_list.append(user.id)
        q = q.where(ManHourModel.user_id.in_(user_list))


    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': pages.total,
        'data': [item.json() for item in pages.items]
    }


# 获取任务列表，以树状表格显示
@task_api.get("/treetable")
@jwt_required()
# @permission_required(Permission.TASK)
def task_list_as_treetable():
    print('api_url', request.url, request.args)
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=10)
    date_start = request.args.get('start')
    date_end = request.args.get('end')
    user_id = request.args.get('user_id')
    project_id = request.args.get('project_id')
    status = request.args.get('status')
    department_id = request.args.get('department_id')
    if department_id:
        user_id = None

    query = request.args.get('query')
    # 构建查询
    # q = db.select(TaskModel)
    q = db.select(TaskModel).order_by(desc(TaskModel.id)).where(TaskModel.parent_id.is_(None))

    if query == "uncompleted":
        q = q.where(TaskModel.status != "已完成")
    if query == "own":
        q = q.where(TaskModel.owner == current_user)
    if query == "create":
        q = q.where(TaskModel.creator == current_user)

    if project_id:
        q = q.where(TaskModel.project_id == project_id)
    if user_id:
        q = q.where(TaskModel.owner_id == user_id)
    if status and status == 'completed':
        q = q.where(TaskModel.status == "已完成")
    if status and status == 'uncompleted':
        q = q.where(TaskModel.status != "已完成")
    if date_start:
        q = q.where(TaskModel.planned_end_date >= date_start)
    if date_end:
        q = q.where(TaskModel.planned_end_date <= date_end)

    if department_id:
        user_list = []
        users = db.session.execute(db.select(UserModel).where(UserModel.department_id == department_id)).scalars().all()
        for user in users:
            user_list.append(user.id)
        q = q.where(TaskModel.owner_id.in_(user_list))

    print(q)

    task_list = db.session.execute(q).scalars().all()
    print(len(task_list))

    # 分页
    paginated_tasks = db.paginate(q, page=page, per_page=per_page)



    ret = []
    # for child in task_list:
    for child in paginated_tasks:
        child_data = child.json()

        child_data["children"] = []
        if child.children:
            child_data["isParent"] = True
            if query == "uncompleted" or status == 'uncompleted':
                child.children = list(filter(lambda x: x.status != '已完成', child.children))
            for son in child.children:
                try:
                    task_list.remove(son)
                except:
                    pass
                finally:
                    son_data = son.json()

                    child_data['children'].append(son_data)
        ret.append(child_data)
    return {
        "code": 0,
        "message": "数据请求成功！",
        # "count": '',
        "count": paginated_tasks.total,
        "data": ret
        # "data": [item.json() for item in paginated_tasks.items]
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


# 更新父任务（如有）的计划工时
def update_task_planned_man_hours(task):
    if task.planned_man_hours and task.parent_id:

        # 删除任务事务提交后，再执行下行代码后会报错
        parent_task = task.parent
        print(parent_task.children)
        parent_task.planned_man_hours = db.session.query(db.func.sum(TaskModel.planned_man_hours))\
            .filter(TaskModel.parent_id == parent_task.id).scalar()
        parent_task.save()


# 添加任务
@task_api.post('/')
@jwt_required()
def task_add():
    data = request.get_json()
    task = TaskModel()
    task.update(data)
    task.creator_id = current_user.id
    try:
        print('bbbb')
        task.save()
        task.update_parent_date()  # 更新父任务的日期
        task.update_parent_planned_work_hours()  # 更新父任务的计划工时
        # update_task_planned_man_hours(task)
    except Exception as e:
        print('任务添加失败。')
        print(e)
        return {
            'code': -1,
            'msg': '新增数据失败'
        }
    return {
        'code': 0,
        'msg': '新增数据成功'
    }


# 修改任务
@task_api.put('/<int:tid>')
def task_edit(tid):
    data = request.get_json()
    task = db.get_or_404(TaskModel, tid)
    task.update(data)
    try:
        task.save()
        task.update_parent_date()  # 更新父任务的日期
        task.update_parent_planned_work_hours()  # 更新父任务的计划工时
        # update_task_planned_man_hours(task)
    except Exception as e:
        print('任务修改失败')
        print(e)
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


# 删除任务
@task_api.delete('/<int:tid>')
@permission_required('task_delete')
@jwt_required()
def task_delete(tid):
    task: TaskModel = db.get_or_404(TaskModel, tid)
    if task.children:
        # 父任务无法删除
        return {
            'code': -1,
            'msg': "请删除子任务后尝试。"
        }
    if task.creator.name == current_user.name or has_permission('system_admin'):
        # 系统管理员可以删除任务
        # 有权限用户可以删除自己创建的任务
        try:
            pass
            db.session.delete(task)
            task.update_parent_date()  # 更新父任务的日期
            task.update_parent_planned_work_hours()  # 更新父任务的计划工时
            task.update_actual_work_hours()  # 更新任务及父任务的实际工时
        except Exception as e:
            print('任务删除失败')
            print(e)
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
    # q = db.select(ManHourModel).where(ManHourModel.task_id == tid)
    # MHlist = db.session.execute(q).scalars().all()
    task: TaskModel = db.get_or_404(TaskModel, tid)
    MHlist = task.man_hours

    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': "",
        'data': [item.json() for item in MHlist]
    }


# 工时变动（新增、修改、删除）时，同步更新任务（含父任务）的实际总工时
def update_task_actual_man_housr(tid):
    # 更新工时所在任务
    task: TaskModel = db.get_or_404(TaskModel, tid)
    task.actual_man_hours = db.session.query(db.func.sum(ManHourModel.man_hour)) \
        .filter(ManHourModel.task_id == tid).scalar()
    task.save()
    # 更新工时所在任务的父任务（如有）
    if task.parent_id:
        parent_task: TaskModel = db.get_or_404(TaskModel, task.parent_id)
        parent_task.actual_man_hours = db.session.query(db.func.sum(TaskModel.actual_man_hours)) \
            .filter(TaskModel.parent_id == task.parent_id).scalar()
        parent_task.save()


# 工时变动（新增、修改、删除）时，同步更新任务（含父任务）的实际开始日期
def update_task_actual_start_date(tid):
    task: TaskModel = db.get_or_404(TaskModel, tid)
    task.actual_start_date = db.session.query(db.func.min(ManHourModel.work_date)) \
        .filter(ManHourModel.task_id == tid).scalar()
    print(task.actual_start_date)
    task.save()
    # 更新工时所在任务的父任务（如有）
    if task.parent_id:
        parent_task: TaskModel = db.get_or_404(TaskModel, task.parent_id)
        parent_task.actual_start_date = db.session.query(db.func.min(TaskModel.actual_start_date)) \
            .filter(TaskModel.parent_id == task.parent_id).scalar()
        parent_task.save()


# 添加工时
@task_api.post('/<int:tid>/man-hour')
@jwt_required()
def man_hour_add(tid):
    data = request.get_json()
    man_hour = ManHourModel()
    man_hour.update(data)
    man_hour.user_id = current_user.id

    try:
        man_hour.save()
        # update_task_actual_man_housr
        man_hour.task.update_actual_work_hours()  # 更新任务及父任务的实际工时
        update_task_actual_start_date(tid)
    except Exception as e:
        print('工时添加失败')
        print(e)
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
        # update_task_actual_man_housr(tid)
        man_hour.task.update_actual_work_hours()  # 更新任务及父任务的实际工时
        update_task_actual_start_date(tid)
    except Exception as e:
        print('工时修改失败')
        print(e)
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


# 删除工时
@task_api.delete('/<int:tid>/man-hour/<int:mid>')
@jwt_required()
def man_hour_delete(tid, mid):
    man_hour: ManHourModel = db.get_or_404(ManHourModel, mid)
    if man_hour.user == current_user:
        try:
            pass
            db.session.delete(man_hour)
            # db.session.commit()
            # update_task_actual_man_housr(tid)
            man_hour.task.update_actual_work_hours()  # 更新任务及父任务的实际工时
            update_task_actual_start_date(tid)
        except Exception as e:
            print('工时删除失败')
            print(e)
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
            'msg': '只能删除自己创建的工时。'
        }
