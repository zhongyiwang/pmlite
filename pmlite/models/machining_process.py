from datetime import datetime, timedelta
from pmlite.extensions import db
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Text, Enum, UniqueConstraint


from ._base import BaseModel


now = datetime.now()
# 当前月
this_month = (now.year, now.month)
# 上个月
last_month_date = now.replace(day=1) - timedelta(days=1)
last_month = (last_month_date.year, last_month_date.month)
# 上上个月
two_months_ago_date = last_month_date.replace(day=1) - timedelta(days=1)
two_months_ago = (two_months_ago_date.year, two_months_ago_date.month)


# 工艺方案
class MachiningProcessModel(BaseModel):
    __tablename__ = 'machining_process'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    number = Column(String(10), comment='项目编号')
    customer = Column(String(50), comment='客户名称')
    workpiece = Column(String(20), comment='工件名称')
    material = Column(String(20), comment='工件材质')
    work_shape = Column(String(50), comment='工件形状')
    customer_industry = Column(String(50), comment='客户行业')
    project_type = Column(String(50), comment='项目类型')
    machine_type = Column(String(50), comment='机床型号')
    receive_date = Column(DateTime, comment='方案接收日期')
    required_date = Column(DateTime, comment='要求完成日期')

    manager_id = Column(Integer, ForeignKey("user.id"), comment="项目负责人")
    manager = db.relationship("UserModel", backref="mp_projects")

    initial_done_date = Column(DateTime, comment='方案首次完成日期')
    last_done_date = Column(DateTime, comment='方案最新更新日期')
    is_delay = Column(Boolean, default=False, comment='方案有无拖期')
    delay_reason = Column(String(100), comment='拖期原因')
    delay_countermeasure = Column(String(50), comment='拖期对策')
    turn_key = Column(Boolean, default=False, comment='是否交钥匙')
    is_automation = Column(Boolean, default=False, comment='是否自动化')
    sales_manager = Column(String(10), comment='销售经理')
    area = Column(String(20), comment='区域')
    agent = Column(String(20), comment='代理商')

    pause_reason = Column(String(100), comment='暂停原因')
    lose_reason = Column(String(100), comment='丢单原因')
    lose_competitor = Column(String(50), comment='丢单竞争对手')
    suggest = Column(String(100), comment='建议及对策')

    created_at = Column(DateTime, default=datetime.now, comment='创建日期')

    # 关系定义：一个项目有多个月度状态记录
    monthly_statuses = db.relationship('MachiningProcessStatusModel', backref='project', lazy=True)

    def __repr__(self):
        return "<MachiningProcess %r>" % self.customer

    def json(self):
        return {
            "id": self.id,
            "number": self.number,
            "customer": self.customer,
            "workpiece": self.workpiece,
            "material": self.material,
            "work_shape": self.work_shape,
            "customer_industry": self.customer_industry,
            "project_type": self.project_type,
            "machine_type": self.machine_type,
            "receive_date": self.receive_date.strftime("%Y-%m-%d") if self.receive_date else "",
            "required_date": self.required_date.strftime("%Y-%m-%d") if self.required_date else "",
            "manager_id": self.manager_id,
            "manager": self.manager.name,
            "initial_done_date": self.initial_done_date.strftime("%Y-%m-%d") if self.initial_done_date else "",
            "last_done_date": self.last_done_date.strftime("%Y-%m-%d") if self.last_done_date else "",
            "is_delay": self.is_delay,
            "delay_reason": self.delay_reason,
            "delay_countermeasure": self.delay_countermeasure,
            "turn_key": self.turn_key,
            "is_automation": self.is_automation,
            "sales_manager": self.sales_manager,
            "area": self.area,
            "agent": self.agent,
            "pause_reason": self.pause_reason,
            "lose_reason": self.lose_reason,
            "lose_competitor": self.lose_competitor,
            "suggest": self.suggest,
            "created_at": self.created_at,
            'this_month': [item.status for item in self.monthly_statuses if item.year == this_month[0] and item.month == this_month[1]],
            'last_month': [item.status for item in self.monthly_statuses if item.year == last_month[0] and item.month == last_month[1]],
            'two_months_ago': [item.status for item in self.monthly_statuses if item.year == two_months_ago[0] and item.month == two_months_ago[1]],
        }


# 工艺方案状态
class MachiningProcessStatusModel(BaseModel):
    __tablename__ = 'machining_process_status'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    year = Column(Integer, nullable=False, comment='年份')
    month = Column(Integer, nullable=False, comment='月份份')
    status = Column(String(10), nullable=False, comment='状态：在谈/暂停/成交/丢单')
    notes = db.Column(Text, comment='备注')
    update_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="创建日期")

    # 外键关联项目
    project_id = Column(Integer, ForeignKey('machining_process.id'), nullable=False)

    # 定义联合唯一约束，确保每个项目每个月只有1条记录
    __table_args__ = (
        UniqueConstraint('project_id', 'year', 'month', name='uq_project_month'),
    )

    # 添加了period属性，方便以"YYYY-MM"格式显示月份
    @property
    def period(self):
        return f"{self.year}-{self.month: 02d}"

    def __repr__(self):
        return f'<MachiningProcessStatus {self.period} for {self.project.customer}: {self.status}>'


# 工件形状
class WorkShapeModel(BaseModel):
    __tablename__ = 'work_shape'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    name = Column(String(50), nullable=False, comment='工件形状名称')
    remark = Column(String(50), comment='备注')

    def __repr__(self):
        return "<WorkShape %r>" % self.name

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "remark": self.remark
        }


# 客户行业
class CustomerIndustryModel(BaseModel):
    __tablename__ = 'customer_industry'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    name = Column(String(50), nullable=False, comment='客户行业名称')
    remark = Column(String(50), comment='备注')

    def __repr__(self):
        return "<CustomerIndustry %r>" % self.name

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "remark": self.remark
        }


# 项目类型
class ProjectTypeModel(BaseModel):
    __tablename__ = 'project_type'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    name = Column(String(50), nullable=False, comment='项目类型名称')
    remark = Column(String(50), comment='备注')

    def __repr__(self):
        return "<ProjectType %r>" % self.name

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "remark": self.remark
        }

