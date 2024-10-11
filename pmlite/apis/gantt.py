from flask import Blueprint, request
from ..extensions import db
from ..models import TaskModel

gantt_api = Blueprint("gantt", __name__, url_prefix="/gantt")


# 项目甘特图,返回该项目下所有任务的甘特图
@gantt_api.route("/project/<int:pid>")
def gantt_view(pid):
    q = db.select(TaskModel).where(TaskModel.project_id == pid)
    tasks = db.session.execute(q).scalars().all()
    task_list = []
    for task in tasks:
        if task.planned_start_date and task.planned_end_date:
            task_data = task.json()
            task_obj = {}
            task_obj['name'] = task_data['title']
            task_obj['desc'] = ""
            task_obj['values'] = [{
                "from": task_data['planned_start_date'],
                "to": task_data['planned_end_date']
            }]
            task_list.append(task_obj)
    return task_list


# 用户甘特图，返回用户的未完成任务甘特图
@gantt_api.route("/user/<int:uid>")
def user_gantt_view(uid):
    q = db.select(TaskModel).where(TaskModel.owner_id == uid).where(TaskModel.status != "已完成")
    tasks = db.session.execute(q).scalars().all()
    task_list = []
    for task in tasks:
        if task.planned_start_date and task.planned_end_date:
            task_data = task.json()
            task_obj = {}
            task_obj['name'] = task_data['title']
            task_obj['desc'] = ""
            task_obj['values'] = [{
                "from": task_data['planned_start_date'],
                "to": task_data['planned_end_date']
            }]
            task_list.append(task_obj)
    return task_list