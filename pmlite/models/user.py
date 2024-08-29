from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from pmlite.extensions import db
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
# from .project import project_user_table

from ._base import BaseModel
from .task import user_task


class UserModel(BaseModel):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    number = Column(String(10), nullable=False, unique=True, comment="员工编号")
    name = Column(String(20), nullable=False, comment="姓名")
    mobile = Column(String(11), nullable=False, unique=True, comment="手机号码")
    mobile_short = Column(String(11), unique=True, comment="集团短号")
    email = Column(String(50), nullable=False, unique=True, comment="邮箱")
    disabled = Column(Boolean, default=False, comment="禁用")
    password_hash = Column(String(256), nullable=False, comment="密码hash")

    create_time = Column(DateTime, default=datetime.now, comment="创建日期")

    department_id = Column(Integer, ForeignKey("department.id"), comment="部门id")
    department = db.relationship("DepartmentModel", backref="users")

    # own_tasks = db.relationship('TaskModel', secondary=user_task, back_populates='owners')

    def __repr__(self):
        return '<User %r>' % self.name

    def json(self):
        return {
            "id": self.id,
            "number": self.number,
            "name": self.name,
            "mobile": self.mobile,
            "mobile_short": self.mobile_short,
            "email": self.email,
            "disabled": self.disabled,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "department": self.department.name
        }

    def __init__(self, *args, **kwargs):
        pass
        """
        if "password" in kwargs:
            self.password = kwargs.get("password")
            kwargs.pop("password")
        super(UserModel, self).__init__(*args, **kwargs)
        """

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)
