from datetime import datetime
from pmlite.extensions import db
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Text, Enum, Float
from sqlalchemy.event import listens_for
from ._base import BaseModel, StatusEnum



class TaskTypeModel(BaseModel):
    __tablename__ = 'task_type'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    name = Column(String(50), nullable=False, comment='任务类型')

    def __repr__(self):
        return "<TaskType %r>" % self.name

    def json(self):
        return {
            "id": self.id,
            "name": self.name
        }


user_task = db.Table('user_task',
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('task_id', Integer, ForeignKey('task.id'), primary_key=True)
)


class ManHourModel(BaseModel):
    __tablename__ = 'man-hour'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    work_date = Column(DateTime, nullable=False, comment='日期')
    man_hour = Column(Float, comment='工时数')
    content = Column(String(50), comment='工时内容')

    task_id = Column(Integer, ForeignKey("task.id"), comment='任务id')
    task = db.relationship("TaskModel", backref=db.backref("man_hours", cascade="all"))

    user_id = Column(Integer, ForeignKey("user.id"), comment='用户id')
    user = db.relationship("UserModel", backref="man_hours")

    def json(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task": self.task.title,
            "user_id": self.user_id,
            "user": self.user.name,
            "work_date": self.work_date.strftime("%Y-%m-%d") if self.work_date else "",
            "man_hour": self.man_hour,
            "content": self.content
        }


class TaskModel(BaseModel):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    title = Column(String(50), nullable=False, comment='任务标题')
    planned_start_date = Column(DateTime, comment='计划开始日期')
    planned_end_date = Column(DateTime, comment='计划完成日期')
    actual_start_date = Column(DateTime, comment='实际开始日期')
    actual_end_date = Column(DateTime, comment='实际完成日期')
    status = Column(Enum("未开始", "进行中", "已完成"), default="未开始", comment='完成状态')
    planned_man_hours = Column(Float, comment='计划工时')
    actual_man_hours = Column(Float, comment='实际工时')

    project_id = Column(Integer, ForeignKey("project.id"), comment='项目id')
    project = db.relationship("ProjectModel", backref="tasks")

    task_type_id = Column(Integer, ForeignKey("task_type.id"), comment='任务类型id')
    task_type = db.relationship("TaskTypeModel", backref='tasks')

    creator_id = Column(Integer, ForeignKey("user.id"))
    creator = db.relationship("UserModel", backref="created_tasks", foreign_keys=[creator_id])

    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = db.relationship("UserModel", backref="own_tasks", foreign_keys=[owner_id])

    # owners = db.relationship('UserModel', secondary=user_task, back_populates='own_tasks')

    parent_id = Column(Integer, ForeignKey('task.id'), default=None, comment='上级任务id')
    parent = db.relationship('TaskModel', back_populates='children', remote_side=[id])
    children = db.relationship('TaskModel', back_populates='parent', cascade='all')

    def __repr__(self):
        return "<Task %r>" % self.title

    # 更新父任务的日期
    def update_parent_date(self):
        if self.parent:
            sub_tasks = self.parent.children
            # 更新父任务的计划开始日期为所有子任务中最早的计划开始日期
            if any(task.planned_start_date for task in sub_tasks):
                earliest_planned_start = min([task.planned_start_date for task in sub_tasks if task.planned_start_date])
                self.parent.planned_start_date = earliest_planned_start
            else:
                self.parent.planned_start_date = None

            # 更新父任务的计划结束日期为所有子任务中最晚的计划结束日期
            if any(task.planned_end_date for task in sub_tasks):
                latest_planned_end = max([task.planned_end_date for task in sub_tasks if task.planned_end_date])
                self.parent.planned_end_date = latest_planned_end
            else:
                self.parent.planned_end_date = None

            # 更新父任务的实际开始日期为所有子任务中最早的实际开始日期
            if any(task.actual_start_date for task in sub_tasks):
                earliest_actual_start = min([task.actual_start_date for task in sub_tasks if task.actual_start_date])
                self.parent.actual_start_date = earliest_actual_start
            else:
                self.parent.actual_start_date = None

            # 更新父任务的实际结束日期为所有子任务中最晚的实际结束日期
            if any(task.actual_end_date for task in sub_tasks):
                latest_actual_end = max([task.actual_end_date for task in sub_tasks if task.actual_end_date])
                self.parent.actual_end_date = latest_actual_end
            else:
                self.parent.actual_end_date = None

            db.session.commit()

    # 更新父任务的计划工时
    def update_parent_planned_work_hours(self):
        if self.parent:
            # sub_tasks = self.parent.children
            total_hours = sum([task.planned_man_hours for task in self.parent.children if task.planned_man_hours])
            self.parent.planned_man_hours = total_hours
            db.session.commit()

    # 更新任务及父任务的实际工时
    def update_actual_work_hours(self):
        total_hours = sum([wh.man_hour for wh in self.man_hours if wh.man_hour])
        self.actual_man_hours = total_hours
        if self.parent:
            parent_total_hours = sum([task.actual_man_hours for task in self.parent.children if task.actual_man_hours])
            self.parent.actual_man_hours = parent_total_hours
        db.session.commit()

    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "planned_start_date": self.planned_start_date.strftime("%Y-%m-%d") if self.planned_start_date else "",
            "planned_end_date": self.planned_end_date.strftime("%Y-%m-%d") if self.planned_end_date else "",
            "actual_start_date": self.actual_start_date.strftime("%Y-%m-%d") if self.actual_start_date else "",
            "actual_end_date": self.actual_end_date.strftime("%Y-%m-%d") if self.actual_end_date else "",
            "status": self.status,
            "planned_man_hours": self.planned_man_hours,
            "actual_man_hours": self.actual_man_hours,
            "project_id": self.project_id,
            "project": self.project.name if self.project else "",
            "task_type": self.task_type.name if self.task_type else "",
            "creator": self.creator.name if self.creator else "",
            "owner_id": self.owner_id,
            "owner": self.owner.name if self.owner else "",
            "parent_id": self.parent_id,
            "is_parent": True if self.children else False
        }

    @classmethod
    def update_parent_status(cls, parent_task):
        # 检查所有子任务是否都已完成
        all_children_completed = all(child.status == "已完成" for child in parent_task.children)
        if all_children_completed:
            parent_task.status = "已完成"
            db.session.commit()


# @listens_for(TaskModel, 'after_insert')
# @listens_for(TaskModel, 'after_update')
# @listens_for(TaskModel, 'after_delete')
# def update_parent(mapper, connection, target):
#     print('aaaaa')
#     target.update_parent_planned_work_hours()