import datetime

from flask import Blueprint, request
from sqlalchemy import desc, or_
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required, get_jwt_identity

from ..models import ProjectModel, ProjectNodeModel, ProjectNodeTitleModel, TaskModel, ManHourModel, ProjectPlanVersionModel, ProjectPlanSignatureModel
from ..extensions import db
from ..decorators import permission_required


project_api = Blueprint("project", __name__, url_prefix="/project")


# 获取项目列表，以分页的形式显示
@project_api.route('/')
@jwt_required()
def project_view():
    print(get_jwt_identity())
    print(current_user)
    # 分页查询字符串
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=30)
    # 自定义查询字符串
    show_all = request.args.get('showAll')
    customer = request.args.get('customer')
    mine = request.args.get('mine')

    q = db.select(ProjectModel).order_by(desc(ProjectModel.id))

    if not show_all:  # 默认获取未完成项目
        q = q.filter(ProjectModel.is_close.isnot(True))

    if customer:  # 外部查询，模糊查询客户字段
        page = 1  # 避免在选择分页后查询报警，查询默认显示第1页数据
        q = q.filter(ProjectModel.customer.like('%' + customer + '%'))

    if mine:
        q = q.filter(or_(ProjectModel.manager_id == current_user.id,
                        ProjectModel.m_designer_id == current_user.id,
                        ProjectModel.e_designer_id == current_user.id,
                        ProjectModel.am_designer_id == current_user.id,
                        ProjectModel.ae_designer_id == current_user.id,))

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    print(pages.items)
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': pages.total,
        'data': [item.json() for item in pages.items]
    }


# 获取项目列表，分页显示(弃用）
@project_api.route('/pagination')
def project_view_pagination():
    status = request.args.get('status')
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=30)

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


# 获取自动化项目列表，以分页的形式显示
@project_api.route('/automation')
def project_automation_view():
    # 分页查询字符串
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=30)
    # 自定义查询字符串
    show_all = request.args.get('showAll')
    customer = request.args.get('customer')

    q = db.select(ProjectModel).filter(ProjectModel.is_automation.is_(True)).order_by(desc(ProjectModel.id))

    if not show_all:  # 默认获取未完成项目
        q = q.filter(ProjectModel.is_close.isnot(True))

    if customer:  # 外部查询，模糊查询客户字段
        page = 1  # 避免在选择分页后查询报警，查询默认显示第1页数据
        q = q.filter(ProjectModel.customer.like('%' + customer + '%'))

    projects: Pagination = db.paginate(q, page=page, per_page=per_page)

    ret = []
    for project in projects:
        project_data = project.json()
        node_data = {}
        nodes = db.session.execute(db.select(ProjectNodeModel).filter(
            ProjectNodeModel.project_id == project.id,
            ProjectNodeModel.version == project.plan_version
        )).scalars().all()
        for node in nodes:
            # node_data[node.node_id] = node.planned_end_date
            node_data[node.node_id] = node.json()['planned_end_date']
        project_data['internal_check_date'] = node_data.get(12)
        project_data['external_check_date1'] = node_data.get(13)
        project_data['external_check_date2'] = node_data.get(14)
        project_data['am_drawing_date1'] = node_data.get(21)
        project_data['am_drawing_date2'] = node_data.get(22)
        project_data['am_drawing_date3'] = node_data.get(23)
        project_data['ae_drawing_date'] = node_data.get(24)
        project_data['arrival_date'] = node_data.get(32)

        # project_data['internal_check_date'] = node_data[12] if node_data[12] else ""
        # project_data['external_check_date1'] = node_data[13] if node_data[13] else ""
        # project_data['external_check_date2'] = node_data[14] if node_data[14] else ""

        ret.append(project_data)
        # break

    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': projects.total,
        'data': ret
        # 'data': [item.json() for item in projects.items]
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
        # child_data['actual_man_hours'] = db.session.query(db.func.sum(ManHourModel.man_hour)) \
        #     .filter(ManHourModel.task_id == child.id).scalar()
        # if isinstance(child_data['actual_man_hours'], float):
        #     child_data['actual_man_hours'] = round(child_data['actual_man_hours'], 1)

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
                    # son_data['actual_man_hours'] = db.session.query(db.func.sum(ManHourModel.man_hour)) \
                    #     .filter(ManHourModel.task_id == son.id).scalar()
                    # if isinstance(son_data['actual_man_hours'], float):
                    #     son_data['actual_man_hours'] = round(son_data['actual_man_hours'], 1)

                    child_data['children'].append(son_data)
        ret.append(child_data)
    print(ret)
    return {
        "code": 0,
        "message": "数据请求成功！",
        "count": '',
        "data": ret
    }


# 创建新项目，同时创建项目计划
@project_api.post('/')
# @jwt_required()
@permission_required('create_project')
def project_add():
    data = request.get_json()
    project = ProjectModel()
    project.update(data)
    project.creator = current_user
    try:
        project.save()
        project.add_initial_plan()  # 创建初版的项目计划
        project.add_initial_plan_version()  # 创建1个项目计划版本
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
    print(pid)
    project = db.get_or_404(ProjectModel, pid)
    print(project. creator)
    if project.creator == current_user:
        try:
            db.session.delete(project)
            # user.is_del = True
            db.session.commit()
        except Exception as e:
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
            'msg': '只能删除自己创建的项目'
        }


# 添加项目节点
# @project_api.post('/node')
@project_api.post('/node/<int:project_id>')
# @jwt_required()
def project_node_add(project_id):
    # 获取所有的节点标题(父节点）
    nodes = db.session.execute(db.select(ProjectNodeTitleModel).where(ProjectNodeTitleModel.parent_id.is_(None))).scalars().all()

    for node in nodes:
        # 保存父节点
        node_data = {
            "name": node.name,
            "node_id": node.node_id,
            "project_id": project_id
        }
        project_node = ProjectNodeModel()
        project_node.update(node_data)
        project_node.save()

        # 保存子节点
        if node.children:
            current_project_node = db.session.execute(
                db.select(ProjectNodeModel).filter(ProjectNodeModel.project_id == project_id,
                                                   ProjectNodeModel.node_id == node.node_id)).scalar()
            for sub_node in node.children:
                sub_node_data = {
                    "name": sub_node.name,
                    "node_id": sub_node.node_id,
                    "project_id": project_id
                }
                sub_project_node = ProjectNodeModel()
                sub_project_node.update(sub_node_data)
                sub_project_node.parent = current_project_node
                sub_project_node.save()


# 添加项目节点，版本升级
# @project_api.post('/node')
@project_api.get('/plan/<int:project_id>')
# @jwt_required()
def project_plan_add(project_id):
    # 获取当前项目的计划版本
    project: ProjectModel = db.get_or_404(ProjectModel, project_id)
    current_version = project.plan_version
    new_version = current_version + 1

    # 获取当前项目计划的父节点信息
    q = db.select(ProjectNodeModel).filter(ProjectNodeModel.project_id == project_id,
                                           ProjectNodeModel.parent_id.is_(None))
    nodes = db.session.execute(q).scalars().all()

    for node in nodes:
        # 创建父节点，复制原节点数据
        node_data = {
            "name": node.name,
            "node_id": node.node_id,
            "project_id": project_id,
            "planned_start_date": node.planned_start_date,
            "planned_end_date": node.planned_end_date,
            "planned_period": node.planned_period,
            "actual_start_date": node.actual_start_date,
            "actual_end_date": node.actual_end_date,
            "actual_period": node.actual_period,
            "remark": node.remark,
            "version": current_version + 1,
            "owner": node.owner
        }
        project_node = ProjectNodeModel()
        project_node.update(node_data)
        project_node.save()

        # 创建子阶段，并复制原节点数据
        if node.children:
            # 找到刚刚新创建的父节点
            current_project_node = db.session.execute(
                db.select(ProjectNodeModel).filter(ProjectNodeModel.project_id == project_id,
                                                   ProjectNodeModel.node_id == node.node_id),
                ProjectNodeModel.version == new_version).scalar()
            for sub_node in node.children:
                sub_node_data = {
                    "name": sub_node.name,
                    "node_id": sub_node.node_id,
                    "project_id": project_id,
                    "planned_start_date": sub_node.planned_start_date,
                    "planned_end_date": sub_node.planned_end_date,
                    "planned_period": sub_node.planned_period,
                    "actual_start_date": sub_node.actual_start_date,
                    "actual_end_date": sub_node.actual_end_date,
                    "actual_period": sub_node.actual_period,
                    "remark": sub_node.remark,
                    "version": current_version + 1,
                    "owner": sub_node.owner
                }
                sub_project_node = ProjectNodeModel()
                sub_project_node.update(sub_node_data)
                sub_project_node.parent = current_project_node
                sub_project_node.save()

    project.plan_version = new_version
    project.save()


    return {
        '版本': current_version
    }

    # user: UserModel = db.get_or_404(UserModel, uid)
'''    
    # 获取所有的节点项目(父节点）
    nodes = db.session.execute(db.select(ProjectNodeTitleModel).where(ProjectNodeTitleModel.parent_id.is_(None))).scalars().all()

    for node in nodes:
        # 保存父节点
        node_data = {
            "name": node.name,
            "node_id": node.node_id,
            "project_id": project_id
        }
        project_node = ProjectNodeModel()
        project_node.update(node_data)
        project_node.save()

        # 保存子节点
        if node.children:
            current_project_node = db.session.execute(
                db.select(ProjectNodeModel).filter(ProjectNodeModel.project_id == project_id,
                                                   ProjectNodeModel.node_id == node.node_id)).scalar()
            for sub_node in node.children:
                sub_node_data = {
                    "name": sub_node.name,
                    "node_id": sub_node.node_id,
                    "project_id": project_id
                }
                sub_project_node = ProjectNodeModel()
                sub_project_node.update(sub_node_data)
                sub_project_node.parent = current_project_node
                sub_project_node.save()
'''


# 根据项目id查询该项目下的计划的节点信息
# @project_api.get('/node/<int:project_id>')
@project_api.get('/<int:project_id>/node')
# @jwt_required()
def project_node_detail(project_id):
    # 获取请求url的版本信息，默认版本时，默认为1
    version = request.args.get('version')

    # 构建查询，该项目id下的所有父节点(过滤版本信息)
    q = db.select(ProjectNodeModel).filter(
        ProjectNodeModel.project_id == project_id,
        ProjectNodeModel.version == version,
        ProjectNodeModel.parent_id.is_(None))
    nodes = db.session.execute(q).scalars().all()
    ret = []
    # 遍历父节点，添加每个父节点下的子节点
    for node in nodes:
        node_data = node.json()
        node_data["children"] = []
        if node.children:
            node_data["isParent"] = True
        for sub_node in node.children:
            sub_node_data = sub_node.json()
            node_data["children"].append(sub_node_data)
        ret.append(node_data)
    return {
        "code": 0,
        "count": len(ret),
        "message": "数据请求成功！",
        "data": ret
    }


# 修改项目的节点计划信息
@project_api.put('/node/<int:project_node_id>')
def project_node_edit(project_node_id):
    data = request.get_json()
    field = data['field']
    value = data['value']
    update = data['update']
    print(field, value, update)

    project_node = db.get_or_404(ProjectNodeModel, project_node_id)
    project_node.update(update)
    try:
        project_node.save()
        if field in ['planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date']:
            project_node.calculate_period()
            # db.session.commit()
            project_node.update_parent_node()
            # db.session.commit()
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


# 项目节点标题
# 获取项目节点标题，已树状表格显示
@project_api.get('/node_title')
def node_title_view():
    # 查询所有父节点
    q = db.select(ProjectNodeTitleModel).filter(ProjectNodeTitleModel.parent_id.is_(None))
    parent_nodes = db.session.execute(q).scalars().all()

    ret = []
    for node in parent_nodes:
        data = node.json()
        data["isParent"] = True
        data["children"] = []
        for child in node.children:
            child_data = child.json()
            data['children'].append(child_data)
        ret.append(data)
    return {
        "code": 0,
        "message": "数据请求成功！",
        "data": ret
    }


# 添加项目节点标题
@project_api.post('/node_title')
def node_title_add():
    data = request.get_json()
    node_title = ProjectNodeTitleModel()
    node_title.update(data)
    try:
        node_title.save()
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


# 修改项目节点标题
@project_api.put('/node_title/<int:nt_id>')
def node_title_edit(nt_id):
    data = request.get_json()
    print(data)
    node_title = db.get_or_404(ProjectNodeTitleModel, nt_id)
    node_title.update(data)
    try:
        node_title.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


# 删除项目节点标题
@project_api.delete('/node_title/<int:nt_id>')
def node_title_delete(nt_id):
    node_title: ProjectNodeTitleModel = db.get_or_404(ProjectNodeTitleModel, nt_id)
    if node_title is None:
        return {
            'code': -1,
            'msg': '为找到数据。'
        }
    if not node_title.can_delete():
        return {
            'code': -1,
            'msg': '请删除子任务后重试！'
        }
    try:
        db.session.delete(node_title)
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


# 项目计划版本列表
@project_api.get('/plan_version')
def project_plan_version_view():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=20)
    q = db.select(ProjectPlanVersionModel)

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)
    ret = []
    for item in pages.items:
        item_ret = item.json()
        project_id = item.json()['project_id']
        plan_version = item.json()['plan_version']
        q = db.select(ProjectPlanSignatureModel).filter(ProjectPlanSignatureModel.project_id == project_id,
                                                        ProjectPlanSignatureModel.plan_version == plan_version)
        signatures = db.session.execute(q).scalars()
        signed_user = []
        for signature in signatures:
            signed_user.append(signature.user.name)
        item_ret.update({
            'signed_users': ','.join(signed_user)
        })
        ret.append(item_ret)


    return {
        'code': 0,
        'msg': '信息查询成功！',
        'count': pages.total,
        # 'data': [item.json() for item in pages.items]
        'data': ret
    }


# 项目计划版本修改
@project_api.put('/plan_version/<int:pv_id>')
def plan_version_edit(pv_id):
    print('aaa')
    data = request.get_json()
    print(data)
    plan_version = db.get_or_404(ProjectPlanVersionModel, pv_id)
    plan_version.update(data)
    if data["is_released"]:
        plan_version.release_date = datetime.datetime.now()
    else:
        plan_version.release_date = None
    try:
        plan_version.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


# 项目计划签章
@project_api.get('/plan_signature')
def project_plan_signature_view():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=20)
    q = db.select(ProjectPlanSignatureModel)

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    return {
        'code': 0,
        'msg': '信息查询成功！',
        'count': pages.total,
        'data': [item.json() for item in pages.items]
    }
