from datetime import datetime
from pmlite.extensions import db
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Text, Enum, Float

from ._base import BaseModel


class SupplierModel(BaseModel):
    __tablename__ = "supplier"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    name = Column(String(50), nullable=False, unique=True, comment="名称")
    contact = Column(String(10), nullable=False, comment="联系人")
    mobile = Column(String(11), nullable=False, comment="手机号码")
    email = Column(String(11), comment="邮箱地址")
    fax = Column(String(15), comment="传真")
    address = Column(String(100), comment="地址")
    postal_code = Column(String(6), comment="邮政编码")
    long_term = Column(Boolean, default=False, comment="长期合作")
    disabled = Column(Boolean, default=False, comment="禁用")
    create_time = Column(DateTime, default=datetime.now, comment="创建日期")

    def __repr__(self):
        return '<Supplier %r>' % self.name

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact": self.contact,
            "mobile": self.mobile,
            "email": self.email,
            "fax": self.fax,
            "address": self.address,
            "postal_code": self.postal_code,
            "long_term": self.long_term,
            "disabled": self.disabled,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

