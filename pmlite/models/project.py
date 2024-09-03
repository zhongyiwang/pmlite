from datetime import datetime
from pmlite.extensions import db
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Text, Enum

from ._base import BaseModel, StatusEnum, LineTypeEnum
from .machine import MachineTypeModel


class ProjectModel(BaseModel):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    name = Column(String(50), comment='项目名称')
    contract = Column(String(20), comment='合同编号')
    customer = Column(String(50), comment='客户名称')
    workpiece = Column(String(20), comment='工件名称')
    line_type = Column(Enum(LineTypeEnum), default=LineTypeEnum.default, comment="自动线类型")
    # status = Column(Enum(StatusEnum), default=StatusEnum.pending, comment='完成状态')
    status = Column(Enum("未开始", "进行中", "已完成"), default="未开始", comment='完成状态')
    remark = Column(Text, comment='项目描述')

    internal_check_date = Column(DateTime, comment='内审日期')
    external_check_date = Column(DateTime, comment='外审日期')

    drawing_date1 = Column(DateTime, comment='出图日期1')
    drawing_date2 = Column(DateTime, comment='出图日期2')
    drawing_date3 = Column(DateTime, comment='出图日期3')

    arrival_date = Column(DateTime, comment='要求到货日期')

    machine_id = Column(Integer, ForeignKey("machine_type.id"), comment="机型id")
    machine_type = db.relationship("MachineTypeModel", backref="projects")

    designer_id = Column(Integer, ForeignKey("user.id"), comment="自动化设计")
    designer = db.relationship("UserModel", backref="d_projects", foreign_keys=[designer_id])

    creator_id = Column(Integer, ForeignKey("user.id"), comment="创建者")
    creator = db.relationship("UserModel", backref="c_projects", foreign_keys=[creator_id])

    manager_id = Column(Integer, ForeignKey("user.id"), comment="项目经理")
    manager = db.relationship("UserModel", backref="m_projects", foreign_keys=[manager_id])

    def __repr__(self):
        return "<Project %r>" % self.name

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "contract": self.contract,
            "customer": self.customer,
            "workpiece": self.workpiece,
            "line_type": self.line_type.value,
            "status": self.status,
            "remark": self.remark,
            "internal_check_date": self.internal_check_date.strftime("%Y-%m-%d") if self.internal_check_date else "",
            "external_check_date": self.external_check_date.strftime("%Y-%m-%d") if self.external_check_date else "",
            "drawing_date1": self.drawing_date1.strftime("%Y-%m-%d") if self.drawing_date1 else "",
            "drawing_date2": self.drawing_date2.strftime("%Y-%m-%d") if self.drawing_date2 else "",
            "drawing_date3": self.drawing_date3.strftime("%Y-%m-%d") if self.drawing_date3 else "",
            "arrival_date": self.arrival_date.strftime("%Y-%m-%d") if self.arrival_date else "",
            "machine_type": self.machine_type.name if self.machine_type else "",
            "designer": self.designer.name if self.designer else "",
            "manager": self.manager.name if self.manager else "",
            "creator": self.creator.name if self.manager else "",
            "creator_id": self.creator_id
        }


