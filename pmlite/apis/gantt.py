from flask import Blueprint, request
from ..extensions import db
from ..models import TaskModel

gantt_api = Blueprint("gantt", __name__, url_prefix="/gantt")


@gantt_api.route("/<int:pid>")
def gantt_view(pid):
    # pid = request.args.get('pid')
    print('pid:', pid)
    q = db.select(TaskModel).where(TaskModel.project_id == pid)
    tasks = db.session.execute(q).scalars().all()
    print(tasks)
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
    print(task_list)
    return task_list
