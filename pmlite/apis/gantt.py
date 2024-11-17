from flask import Blueprint, request
from ..extensions import db
from ..models import TaskModel
import json

gantt_api = Blueprint("gantt", __name__, url_prefix="/gantt")


# 项目甘特图,返回该项目下所有任务的甘特图
@gantt_api.route("/project/<int:pid>")
def gantt_view(pid):
    q = db.select(TaskModel).where(TaskModel.project_id == pid)
    tasks = db.session.execute(q.filter(TaskModel.parent_id.is_(None))).scalars().all()
    print(tasks)
    task_list = []
    for task in tasks:
        if task.planned_start_date and task.planned_end_date:
            task_data = task.json()
            task_obj = {}
            task_obj['name'] = task_data['title']
            task_obj['desc'] = task_data['owner']
            dataObj = {
                "from": task_data['planned_start_date'],
                "to": task_data['planned_end_date'],
                "a_from": task_data['actual_start_date'],
                "a_to": task_data['actual_end_date']
            }
            task_obj['values'] = [{
                "from": task_data['planned_start_date'],
                "to": task_data['planned_end_date'],
                "label": "",
                # "desc": json.dumps(dataObj, indent=4)[1:-1].replace(',', '<br>'),
                "a_from": task_data['actual_start_date'],
                "a_to": task_data['actual_end_date'],
                "customClass": "",

            }]
            task_list.append(task_obj)
        if task.children:
            for sub_task in task.children:
                sub_task_data = sub_task.json()
                sub_task_obj = {}
                sub_task_obj['name'] = sub_task_data['title']
                sub_task_obj['desc'] = task_data['owner']
                sub_task_obj['values'] = [{
                    "from": sub_task_data['planned_start_date'],
                    "to": sub_task_data['planned_end_date'],
                    "a_from": sub_task_data['actual_start_date'],
                    "a_to": sub_task_data['actual_end_date']
                }]
                task_list.append(sub_task_obj)
    print(task_list)
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
                "to": task_data['planned_end_date'],
                "a_from": task_data['actual_start_date'],
                "a_to": task_data['actual_end_date']
            }]
            task_list.append(task_obj)
    return task_list