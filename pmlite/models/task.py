from datetime import datetime
from pmlite.extensions import db
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Text, Enum, Float

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
            "project": self.project.name if self.project else "",
            "task_type": self.task_type.name if self.task_type else "",
            "creator": self.creator.name if self.creator else "",
            "owner": self.owner.name if self.owner else "",
            "parent_id": self.parent_id,
            "is_parent": True if self.children else False
        }

