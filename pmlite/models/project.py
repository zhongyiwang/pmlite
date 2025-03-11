from datetime import datetime
from pmlite.extensions import db
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Text, Enum

from ._base import BaseModel, StatusEnum, LineTypeEnum
from .machine import MachineTypeModel


class ProjectModel(BaseModel):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    customer = Column(String(50), comment='客户名称')
    project_number = Column(String(10), comment='项目编号')
    bom_number = Column(String(10), comment='BOM编码')

    contract = Column(String(20), comment='合同编号')

    workpiece = Column(String(20), comment='工件名称')

    line_type = Column(Enum(LineTypeEnum), default=LineTypeEnum.default, comment="自动线类型")
    # status = Column(Enum(StatusEnum), default=StatusEnum.pending, comment='完成状态')
    status = Column(Enum("未开始", "进行中", "已完成"), default="未开始", comment='完成状态')
    remark = Column(Text, comment='项目描述')

    is_automation = Column(Boolean, default=False, comment='自动化项目')
    product_department = Column(String(10), comment='生产部负责人')
    sales_department = Column(String(10), comment='营业部负责人')

    machine_id = Column(Integer, ForeignKey("machine_type.id"), comment="机型id")
    machine_type = db.relationship("MachineTypeModel", backref="projects")

    m_designer_id = Column(Integer, ForeignKey("user.id"), comment="机械设计")
    m_designer = db.relationship("UserModel", backref='md_projects', foreign_keys=[m_designer_id])

    e_designer_id = Column(Integer, ForeignKey("user.id"), comment="电气设计")
    e_designer = db.relationship("UserModel", backref="ed_projects", foreign_keys=[e_designer_id])

    am_designer_id = Column(Integer, ForeignKey("user.id"), comment="自动化机械设计")
    am_designer = db.relationship("UserModel", backref="amd_projects", foreign_keys=[am_designer_id])

    ae_designer_id = Column(Integer, ForeignKey("user.id"), comment="自动化电气设计")
    ae_designer = db.relationship("UserModel", backref="aed_projects", foreign_keys=[ae_designer_id])

    creator_id = Column(Integer, ForeignKey("user.id"), comment="创建者")
    creator = db.relationship("UserModel", backref="c_projects", foreign_keys=[creator_id])

    manager_id = Column(Integer, ForeignKey("user.id"), comment="项目经理")
    manager = db.relationship("UserModel", backref="m_projects", foreign_keys=[manager_id])

    nodes = db.relationship('ProjectNodeModel', backref='project', lazy=True)

    plan_version = Column(Integer, default=1, comment='计划版本')

    is_close = Column(Boolean, default=False, comment='是否关闭')

    # 以下字段不在使用
    name = Column(String(50), comment='项目名称')

    designer_id = Column(Integer, ForeignKey("user.id"), comment="自动化设计")
    designer = db.relationship("UserModel", backref="d_projects", foreign_keys=[designer_id])

    internal_check_date = Column(DateTime, comment='内审日期')
    external_check_date = Column(DateTime, comment='外审日期')

    drawing_date1 = Column(DateTime, comment='出图日期1')
    drawing_date2 = Column(DateTime, comment='出图日期2')
    drawing_date3 = Column(DateTime, comment='出图日期3')

    arrival_date = Column(DateTime, comment='要求到货日期')

    def __repr__(self):
        return "<Project %r>" % self.name

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "contract": self.contract,
            "customer": self.customer,
            "workpiece": self.workpiece,
            "project_number": self.project_number,
            "bom_number": self.bom_number,
            "is_automation": self.is_automation,
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
            "plan_version": self.plan_version,
            "designer": self.designer.name if self.designer else "",
            "manager": self.manager.name if self.manager else "",
            "m_designer": self.m_designer.name if self.m_designer else "",
            "e_designer": self.e_designer.name if self.e_designer else "",
            "am_designer": self.am_designer.name if self.am_designer else "",
            "ae_designer": self.ae_designer.name if self.ae_designer else "",
            "creator": self.creator.name if self.manager else "",
            "creator_id": self.creator_id,
            "is_released": self.is_released()
        }

    def add_initial_plan(self):
        # 获取所有的节点标题(父节点）
        nodes = db.session.execute(
            db.select(ProjectNodeTitleModel).where(ProjectNodeTitleModel.parent_id.is_(None))).scalars().all()

        for node in nodes:
            # 保存父节点
            node_data = {
                "name": node.name,
                "node_id": node.node_id,
                "project_id": self.id
            }
            project_node = ProjectNodeModel()
            project_node.update(node_data)
            project_node.save()
            # 保存子节点
            if node.children:
                current_project_node = db.session.execute(
                    db.select(ProjectNodeModel).filter(ProjectNodeModel.project_id == self.id,
                                                       ProjectNodeModel.node_id == node.node_id)).scalar()
                for sub_node in node.children:
                    sub_node_data = {
                        "name": sub_node.name,
                        "node_id": sub_node.node_id,
                        "project_id": self.id
                    }
                    sub_project_node = ProjectNodeModel()
                    sub_project_node.update(sub_node_data)
                    sub_project_node.parent = current_project_node
                    sub_project_node.save()

    def add_initial_plan_version(self):
        plan_version = ProjectPlanVersionModel()
        plan_version.project_id = self.id
        plan_version.plan_version = self.plan_version
        plan_version.save()

    def is_released(self):
        # 确认当前计划版本是否已发布
        q = db.select(ProjectPlanVersionModel).filter(ProjectPlanVersionModel.project_id == self.id,
                                                      ProjectPlanVersionModel.plan_version == self.plan_version)
        plan_version = db.session.execute(q).scalar()
        if not plan_version:
            return False
        try:
            return plan_version.is_released
        except Exception as e:
            return False

    def get_nodes(self):
        pass


# 项目状态模型
class ProjectStatusModel(BaseModel):
    __tablename__ = 'project_status'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    m_drawing_end = Column(Boolean, default=False, comment='机械出图完成')
    e_drawing_end = Column(Boolean, default=False, comment='电气出图完成')
    am_drawing_end = Column(Boolean, default=False, comment='自动化机械出图完成')
    ae_drawing_end = Column(Boolean, default=False, comment='自动化电气出图完成')


# 项目计划的节点
class ProjectNodeModel(BaseModel):
    __tablename__ = 'project_node'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    node_id = Column(Integer, comment='节点编号')
    name = Column(String(50), comment='节点名称')
    stage = Column(String(50), comment='所处阶段')
    planned_start_date = Column(DateTime, comment='计划开始日期')
    planned_end_date = Column(DateTime, comment='计划结束日期')
    planned_period = Column(Integer, comment='计划周期')
    actual_start_date = Column(DateTime, comment='实际开始日期')
    actual_end_date = Column(DateTime, comment='实际结束日期')
    actual_period = Column(Integer, comment='实际周期')
    remark = Column(Text, comment='备注')
    version = db.Column(db.Integer, default=1, comment="版本")
    create_at = Column(DateTime, default=datetime.now, comment="创建日期")

    delay_type = Column(Text, comment='延期类型')
    delay_reason = Column(Text, comment='延期说明')
    owner = Column(String(10), comment='负责人')
    is_close = Column(Boolean, default=False, comment='是否关闭')

    project_id = Column(Integer, ForeignKey("project.id"), nullable=False, comment="所属项目id")

    parent_id = Column(Integer, ForeignKey('project_node.id'), default=None, comment='阶段节点id')
    parent = db.relationship('ProjectNodeModel', back_populates='children', remote_side=[id])
    children = db.relationship('ProjectNodeModel', back_populates='parent', cascade='all')

    def __repr__(self):
        return "<ProjectNode %r>" % self.name

    # 计算周期
    def calculate_period(self):
        # 计算计划周期
        if self.planned_end_date and self.planned_start_date:
            self.planned_period = (self.planned_end_date - self.planned_start_date).days + 1
        else:
            self.planned_period = None
        # 计算实际周期
        if self.actual_end_date and self.actual_start_date:
            self.actual_period = (self.actual_end_date - self.actual_start_date).days + 1
        else:
            self.actual_period = None

    # 更新父任务
    def update_parent_node(self):
        if self.parent:
            sub_nodes = self.parent.children
            # 更新父任务的计划开始日期为所有子任务中最早的计划开始日期
            if any(node.planned_start_date for node in sub_nodes):
                earliest_planned_start = min([node.planned_start_date for node in sub_nodes if node.planned_start_date])
                self.parent.planned_start_date = earliest_planned_start
            else:
                self.parent.planned_start_date = None

            # 更新父任务的计划结束日期为所有子任务中最晚的计划结束日期
            if any(node.planned_end_date for node in sub_nodes):
                latest_planned_end = max([node.planned_end_date for node in sub_nodes if node.planned_end_date])
                self.parent.planned_end_date = latest_planned_end
            else:
                self.parent.planned_end_date = None

            # 更新父任务的实际开始日期为所有子任务中最早的实际开始日期
            if any(node.actual_start_date for node in sub_nodes):
                earliest_actual_start = min([node.actual_start_date for node in sub_nodes if node.actual_start_date])
                self.parent.actual_start_date = earliest_actual_start
            else:
                self.parent.actual_start_date = None

            # 更新父任务的实际结束日期为所有子任务中最晚的实际结束日期
            if any(node.actual_end_date for node in sub_nodes):
                latest_actual_end = max([node.actual_end_date for node in sub_nodes if node.actual_end_date])
                self.parent.actual_end_date = latest_actual_end
            else:
                self.parent.actual_end_date = None

            # 计算父任务的周期
            self.parent.calculate_period()

            db.session.commit()

    def json(self):
        return {
            "id": self.id,
            "node_id": self.node_id,
            "name": self.name,
            "stage": self.stage,
            "planned_start_date": self.planned_start_date.strftime("%Y-%m-%d") if self.planned_start_date else "",
            "planned_end_date": self.planned_end_date.strftime("%Y-%m-%d") if self.planned_end_date else "",
            "planned_period": self.planned_period,
            "actual_start_date": self.actual_start_date.strftime("%Y-%m-%d") if self.actual_start_date else "",
            "actual_end_date": self.actual_end_date.strftime("%Y-%m-%d") if self.actual_end_date else "",
            "actual_period": self.actual_period,
            "remark": self.remark,
            "delay_type": self.delay_type,
            "delay_reason": self.delay_reason,
            "owner": self.owner,
            "is_close": self.is_close,
            "parent_id": self.parent_id
        }


# 项目计划的节点标题
class ProjectNodeTitleModel(BaseModel):
    __tablename__ = 'project_node_title'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    node_id = Column(Integer, comment='节点编号')
    name = Column(String(50), comment='节点名称')

    parent_id = Column(Integer, ForeignKey('project_node_title.id'), default=None, comment='节点阶段id')
    parent = db.relationship('ProjectNodeTitleModel', back_populates='children', remote_side=[id])
    children = db.relationship('ProjectNodeTitleModel', back_populates='parent')

    def __repr__(self):
        return "<ProjectNodeTitle %r>" % self.name

    def can_delete(self):
        # 有子任务时无法删除
        return len(self.children) == 0

    def json(self):
        return {
            'id': self.id,
            "node_id": self.node_id,
            'name': self.name,
            'parent_id': self.parent_id
        }

# 项目计划签章表
class ProjectPlanSignatureModel(BaseModel):
    __tablename__ = 'project_plan_signature'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False, comment="所属项目id")
    project = db.relationship('ProjectModel')
    plan_version = Column(Integer, default=1, comment='计划版本')
    user_id = Column(Integer, ForeignKey("user.id"), comment="用户id")
    user = db.relationship("UserModel")
    signature_date = Column(DateTime, default=datetime.now, comment="签章日期")

    def __repr__(self):
        return "<ProjectPlanSignature %r>" % self.project

    def json(self):
        return {
            "id": self.id,
            "project": self.project.customer,
            "plan_version": self.plan_version,
            "user": self.user.name,
            "signature_date": self.signature_date.strftime("%Y-%m-%d") if self.signature_date else "",
        }


# 项目计划版本表
class ProjectPlanVersionModel(BaseModel):
    __tablename__ = 'project_plan_version'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False, comment="所属项目id")
    project = db.relationship('ProjectModel')
    plan_version = Column(Integer, default=1, comment='计划版本')
    status = Column(String(10), default="编辑中", comment='发布状态')
    is_released = Column(Boolean, default=False, comment='已发布')
    release_date = Column(DateTime, comment="发布日期")

    def __repr__(self):
        return "<ProjectPlanVersion %r>" % self.project

    def json(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "project": self.project.customer,
            "plan_version": self.plan_version,
            "status": self.status,
            "is_released": self.is_released,
            "release_date": self.release_date.strftime("%Y-%m-%d") if self.release_date else "",
        }