import enum
from datetime import datetime
from ..extensions import db


class BaseModel(db.Model):
    __abstract__ = True

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, data):
        for key, value in data.items():
            if "date" in key:
                try:
                    value = datetime.strptime(value, "%Y-%m-%d")
                except ValueError as e:
                    value = None
            else:
                if value == "":
                    value = None
            setattr(self, key, value)


class StatusEnum(enum.Enum):
    pending = "未开始",
    processing = "进行中",
    completed = "已完成"

    def __str__(self):
        return self.value


class LineTypeEnum(enum.Enum):
    default = "未分类"
    gl1 = "单机桁架"
    gl2 = "一拖二桁架"
    gl3 = "多台联机桁架"
    robot1 = "固定机器人"
    robot2 = "地轨机器人"
    robot3 = "天轨机器人"

