from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean

from pmlite.extensions import db
from ._base import BaseModel


class DepartmentModel(BaseModel):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    name = Column(String(50), nullable=False, comment="部门名称")
    leader = Column(String(50), comment="部门负责人")
    parent_id = Column(Integer, ForeignKey('department.id'), default=0, comment="上级部门id")
    parent = db.relationship('DepartmentModel', back_populates='children', remote_side=[id])  # 自关联
    children = db.relationship('DepartmentModel', back_populates='parent')

    def __repr__(self):
        return '<Department %r>' % self.name

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "leader": self.leader,
            "parent_id": self.parent_id,
        }
