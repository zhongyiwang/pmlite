from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, Boolean
from ._base import BaseModel


class UnitModel(BaseModel):
    __tablename__ = 'unit'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    number = Column(Integer, comment='单元序号')
    code = Column(String(11), comment='单元编号')
    name = Column(String(50), comment='单元名称')
    type = Column(Enum("特注", "标准"), default="特注", comment='单元类型')
    assembly = Column(String(11), comment='装配图号')
    remark = Column(Text, comment='备注')
    disabled = Column(Boolean, default=False, comment='禁用')
    create_time = Column(DateTime, default=datetime.now, comment='创建日期')

    cost = Column(Integer, comment='未税成本')
    price = Column(Integer, comment='未税报价')
    update_time = Column(DateTime, default=datetime.now, comment='更新日期')

    def __repr__(self):
        return '<Unit %r>' % self.name

    def json(self):
        return {
            "id": self.id,
            "number": self.number,
            "code": self.code,
            "name": self.name,
            "type": self.type,
            "assembly": self.assembly,
            "remark": self.remark,
            "disabled": self.disabled,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "cost": self.cost,
            "price": self.price,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }