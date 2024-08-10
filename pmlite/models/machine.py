from pmlite.extensions import db
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Text, Enum


from ._base import BaseModel


class MachineTypeModel(BaseModel):
    __tablename__ = 'machine_type'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    name = Column(String(50), nullable=False, comment='机型名称')

    def __repr__(self):
        return "<Machine %r>" % self.name

    def json(self):
        return {
            "id": self.id,
            "name": self.name
        }
