import datetime

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import desc, or_, func, select
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required, get_jwt_identity
from apscheduler.triggers.cron import CronTrigger

from ..models import ProjectModel, ProjectNodeModel, ProjectNodeTitleModel, TaskModel, ManHourModel, ProjectPlanVersionModel, ProjectPlanSignatureModel, RoleModel, UserModel
from ..extensions import db
from ..decorators import permission_required
from ..extensions.email_service import EmailService


from flask_mail import Message
from ..extensions import mail

project_api = Blueprint("project", __name__, url_prefix="/project")


@project_api.get('/schedule/<int:hour>/<int:minute>')
# @permission_required('system_admin')
def email_schedule(hour, minute):
    nodes = ProjectNodeModel.get_expected_delay()
    nodes.sort(key=lambda x: x['days'])
    manager_emails = [node['manager_email'] for node in nodes]
    # 邮件列表去空去重
    manager_emails = list({x: None for x in manager_emails if x not in ("", None)}.keys())

    cron_trigger = CronTrigger(hour=hour, minute=minute)
    result = EmailService.send_scheduled_email(
        subject='拖期及临期项目提醒',
        recipients=manager_emails,
        html='<h3>你有拖期或即将临期的项目，请及时登录系统查看。</h3><P>来自项目管理平台PMS</P>',
        trigger=cron_trigger,
        job_id='daily_report'
    )
    print(result)
    return jsonify({
        'code': 0 if result['success'] else -1,
        'msg': result['message'],
        # 'next_run_time': result['next_run_time']
    })





@project_api.get('/email_test')
def email_test():
    result = EmailService.send_email(
        subject='测试邮件',
        recipients=['wangzhongyi@lnmazak.com.cn'],
        html='<h1>这是一封测试邮件</h1><P>来自项目管理平台PMS</P>'
    )
    current_app.logger.info(f"邮件测试结果： {result}")
    return {
        'code': 0 if result['success'] else -1,
        'msg': 'ok'
    }

@project_api.get('email')
def email():
    try:
        msg = Message(
            subject='测试邮件',
            recipients=['wangzhongyi@lnmazak.com.cn'],
            html='<h1>这是一封测试邮件</h1><P>来自项目管理平台PMS</P>'
        )
        mail.send(msg)
        return {
            'msg': "ok"
        }
    except Exception as e:
        print(e)
        return {
            "msg": "no"
        }


# 获取项目列表，以分页的形式显示
@project_api.route('/')
# @jwt_required()
@permission_required('project_view')
def project_view_treetable():
    # print(get_jwt_identity())
    # print(current_user)
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

    # print(pages.items)
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': pages.total,
        'data': [item.json() for item in pages.items]
    }


# 项目：新建
@project_api.post('/')
@permission_required('project_create')
def project_create():
    data = request.get_json()
    print(data)
    project = ProjectModel()
    project.update(data)
    project.creator = current_user  # 绑定创建者
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


# 项目：修改
@project_api.put('/<int:pid>')
@permission_required('project_update')
def project_edit(pid):
    data = request.get_json()
    # print(data)
    project = db.get_or_404(ProjectModel, pid)
    project.update(data)
    try:
        project.save()

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


# 项目：删除
@project_api.delete('/<int:pid>')
@permission_required('project_delete')
def project_delete(pid):
    """
    只能删除项目经理为自己的项目
    项目管理员可以删掉所有项目
    """
    print(pid)
    project = db.get_or_404(ProjectModel, pid)
    print(project. creator)
    if project.manager == current_user or 'project_admin' in [p.name for p in current_user.role.permissions]:
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


# 项目：信息评审
@project_api.post('/info_audit/<int:project_id>')
@permission_required('project_admin')
def project_info_audit(project_id):
    data = request.get_json()
    print(data)
    project = db.get_or_404(ProjectModel, project_id)
    try:
        project.info_audit(data['event'])  # 评审操作
        if data["event"] == "approve":
            # 项目信息评审通过，发送邮件给项目经理提供创建项目计划
            project_created_email(project_id)
    except Exception as e:
        print(e)
        return {
            'code': -1,
            'msg': '操作失败'
        }
    return {
        'code': 0,
        'msg': '操作成功'
    }

# 获取项目列表，分页显示(弃用）
# @project_api.route('/pagination')
# def project_view_pagination():
#     status = request.args.get('status')
#     page = request.args.get('page', type=int, default=1)
#     per_page = request.args.get('limit', type=int, default=30)
#
#     if status == "uncompleted":
#         q = db.select(ProjectModel).where(ProjectModel.status != "已完成")
#     else:
#         q = db.select(ProjectModel)
#
#     pages: Pagination = db.paginate(q, page=page, per_page=per_page)
#
#     return {
#         'code': 0,
#         'msg': '信息查询成功',
#         'count': pages.total,
#         'data': [item.json() for item in pages.items]
#     }


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


# 项目计划: 查看(根据 项目id和项目版本)
@project_api.get('/<int:project_id>/plan/<int:plan_version>')
def plan_view(project_id, plan_version):
    # 如果没有版本传入，默认返回最新的项目计划
    # version = request.args.get('version')
    project: ProjectModel = db.get_or_404(ProjectModel, project_id)
    # current_plan_version = project.current_version
    # max_version = project.get_max_version()

    # 没有传递版本号时，默认显示当前（最新）版本
    # if not version and max_version:
    #     version = max_version

    # 构建查询，该项目id下的所有父节点(过滤版本信息)
    q = db.select(ProjectNodeModel).filter(
        ProjectNodeModel.project_id == project_id,
        ProjectNodeModel.version == plan_version,
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

            if not sub_node.is_used:
                sub_node_data['manager'] = "— —"
                sub_node_data['planned_start_date'] = "— —"
                sub_node_data['planned_end_date'] = "— —"
                sub_node_data['planned_period'] = "— —"
                sub_node_data['actual_start_date'] = "— —"
                sub_node_data['actual_end_date'] = "— —"
            node_data["children"].append(sub_node_data)
        ret.append(node_data)
    return {
        "code": 0,
        "count": len(ret),
        "message": "数据请求成功！",
        "data": ret,
        "plan_version": plan_version,
        "plan_status": project.get_plan_status()
    }


# 项目计划：创建初始版本
@project_api.post('/<int:project_id>/initial_plan_create')
def plan_create(project_id):
    project: ProjectModel = db.get_or_404(ProjectModel, project_id)

    success, message = project.initial_plan_create()
    print(success, message)

    code = 0 if success else -1

    return {
        "code": code,
        "msg": message,
        "plan_version": project.plan_version,
        "plan_status": project.get_plan_status()
    }



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
    #value = data['value']
    update = data['update']
    # print(field, value, update)

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


# 设置节点的【有/无】信息
@project_api.post('/node/set-use')
def set_node_use():
    data = request.get_json()
    # 参数验证
    if not data or 'ids' not in data:
        return {
            'code': -1,
            'msg': '参数错误，无ids参数'
        }
    ids = data['ids']
    is_used = data['is_used']
    if not isinstance(ids, list) or len(ids) == 0:
        return {
            'code': -1,
            'msg': 'idf必须是包含至少1个id的数组'
        }
    nodes = ProjectNodeModel.query.filter(ProjectNodeModel.id.in_(ids)).all()
    if not nodes:
        return {
            'code': -1,
            'msg': '没有找到节点'
        }
    for node in nodes:
        node.is_used = is_used
        # 设置节点【无】时，清空当前节点的日期
        if not is_used:
            node.planned_start_date = None
            node.planned_end_date = None
            node.actual_start_date = None
            node.actual_end_date = None
            node.calculate_period()
        else:  # 子节点设置【有】是，父节点页设置为【有】
            node.parent.is_used = True
        # 无论设置有无，均更新父节点信息
        node.update_parent_node()
        node.save()

    return {
        'code': 0,
        'msg': '操作成功'
    }


# 项目节点：即将拖期（3天）
@project_api.get('/node/expected_delay')
def node_expected_delay():
    user_id = request.args.get('user_id')
    nodes = ProjectNodeModel.get_expected_delay(user_id)
    nodes.sort(key=lambda x: x['days'])
    print(nodes)
    return{
        'code': 0,
        'count': len(nodes),
        "message": "数据请求成功！",
        "data": nodes
    }


# 项目节点：拖期&临期（3天内到期）项目，给负责人发送邮件
# 通过ubuntu系统执行定时任务
@project_api.get('node/email_delay')
def node_email_delay():
    nodes = ProjectNodeModel.get_expected_delay()
    nodes.sort(key=lambda x: x['days'])
    manager_emails = [node['manager_email'] for node in nodes]
    # 邮件列表去空去重
    manager_emails = list({x: None for x in manager_emails if x not in ("", None)}.keys())

    result = EmailService.send_email(
        subject='拖期及临期项目提醒',
        recipients=manager_emails,
        html='<h3>你有拖期或即将临期的项目，请及时登录系统查看。</h3><P>来自项目管理平台PMS</P>'
    )
    return jsonify({
        'code': 0 if result['success'] else -1,
        'msg': result['message'],
    })

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


# 项目计划版本：查看（列表）
@project_api.get('/plan_version')
def plan_version_view():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=20)
    q = db.select(ProjectPlanVersionModel)\
        .order_by(
            desc(ProjectPlanVersionModel.project_id),
            desc(ProjectPlanVersionModel.create_at)
        )

        # .order_by(desc(ProjectPlanVersionModel.create_at))

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


# 项目计划版本：修改（发布/取消发布） 弃用
@project_api.put('/plan_version/<int:plan_version_id>')
def plan_version_update(plan_version_id):
    data = request.get_json()
    plan_version = db.get_or_404(ProjectPlanVersionModel, plan_version_id)
    project = db.get_or_404(ProjectModel, plan_version.project_id)
    plan_version.update(data)
    if data["status"] == "已发布":
        plan_version.release_date = datetime.datetime.now()
        project.status = "执行中"
        # if project.get_max_version(is_released=True) and plan_version.plan_version > project.get_max_version(is_released=True):
        #     project.current_version = plan_version.plan_version
    else:
        plan_version.release_date = None
        project.status = "已审核"
        # project.current_version = project.get_max_version(is_released=True)
    try:
        plan_version.save()
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


# 项目计划版本： 更改状态（根据 项目id， 计划版本）
@project_api.put('/plan_version/status_update')
def plan_version_status_update():
    data = request.get_json()
    print(data)
    project_id = data['project_id']
    version = data['plan_version']
    status = data['status']
    project = db.get_or_404(ProjectModel, project_id)

    if not project_id or not version :
        return {
            'code': -1,
            'msg': '无项目id或计划版本。'
        }
    plan_version = ProjectPlanVersionModel.query.filter(
        ProjectPlanVersionModel.project_id == project_id,
        ProjectPlanVersionModel.plan_version == version
    ).first()
    if not plan_version:
        return {
            'code': -1,
            'msg': "操作失败，请联系管理员。"
        }
    if status == "已发布":
        plan_version.release_date = datetime.datetime.now()
        project.status = "执行中"
    else:
        plan_version.release_date = None
        project.status = "已审核"
    try:
        plan_version.status = status
        plan_version.save()
        project.save()
        # 当项目计划状态变更为已提交时，发送邮件提醒项目经理进行计划评审
        if status == "已提交":
            project_plan_created_email(project_id, version)
    except Exception as e:
        return {
            'code': -1,
            'msg': "操作失败，请联系管理员。"
        }
    return {
        'code': 0,
        'msg': '操作成功'
    }


# 项目计划版本：删除
@project_api.delete('/plan_version/<int:plan_version_id>')
def plan_version_delete(plan_version_id):
    plan_version = db.get_or_404(ProjectPlanVersionModel, plan_version_id)
    project =  db.get_or_404(ProjectModel, plan_version.project_id)
    if plan_version is None:
        return {
            'code': -1,
            'msg': '未找到数据。'
        }
    try:
        db.session.delete(plan_version)  # 删除条目
        db.session.commit()
        project.plan_delete(plan_version.plan_version)  # 删除该项目、该版本的计划节点
    except Exception as e:
        return {
            'code': -1,
            'msg': '删除数据失败'
        }
    return {
        'code': 0,
        'msg': '删除数据成功'
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


# 新建项目评审通过提醒：提醒项目经理创建项目计划
def project_created_email(project_id):
    project = db.get_or_404(ProjectModel, project_id)

    result = EmailService.send_email(
        subject=f'新项目提醒-{project.customer}({project.project_number})',
        recipients=[project.manager.email],
        html=f'<h3>项目：{project.customer}({project.project_number})已创建，请创建项目计划。</h3><P>来自项目管理平台PMS</P>'
    )
    current_app.logger.info(f"邮件测试结果： {result}")
    return {
        'code': 0 if result['success'] else -1,
        'msg': 'ok'
    }


# 项目计划提交提醒：提醒项目管理员评审项目计划
def project_plan_created_email(project_id, plan_version):
    project = db.get_or_404(ProjectModel, project_id)
    print(project)

    # 项目管理员
    stmt = select(RoleModel).where(RoleModel.name == 'project_admin')
    project_managers = db.session.execute(stmt).scalar().users
    project_manager_emails = [manager.email for manager in project_managers if manager.email]
    # print(project_manager_emails)

    # try:
    #     msg = Message(
    #         subject=f'新项目计划提醒-{project.customer}({project.project_number})',
    #         recipients=project_manager_emails,
    #         html=f'<h3>项目：{project.customer}({project.project_number})的项目计划(版本:{plan_version})已提交，请及时审核。</h3><P>来自项目管理平台PMS</P>'
    #     )
    #     mail.send(msg)
    #     return {
    #         'code': 0,
    #         'msg': "操作成功"
    #     }
    # except Exception as e:
    #     print(e)
    #     return {
    #         'code': -1,
    #         "msg": "操作失败，请联络管理员。"
    #     }

    result = EmailService.send_email(
        subject=f'新项目计划提醒-{project.customer}({project.project_number})',
        recipients=project_manager_emails,
        html=f'<h3>项目：{project.customer}({project.project_number})的项目计划(版本:{plan_version})已提交，请及时审核。</h3><P>来自项目管理平台PMS</P>'
    )
    current_app.logger.info(f"邮件测试结果： {result}")
    return {
        'code': 0 if result['success'] else -1,
        'msg': 'ok'
    }