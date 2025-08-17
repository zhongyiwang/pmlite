from datetime import datetime, date, timedelta
from pmlite.extensions import db
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Text, Enum, select, func, or_, and_

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
    isAudited = Column(Boolean, default=False, comment='项目信息审核')

    line_type = Column(Enum(LineTypeEnum), default=LineTypeEnum.default, comment="自动线类型")
    # status = Column(Enum(StatusEnum), default=StatusEnum.pending, comment='完成状态')
    status = Column(Enum("待提交", "已提交", "已审核", "执行中", "已完成", "未开始", "进行中"), default="待提交", comment='完成状态')
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

    nodes = db.relationship('ProjectNodeModel', backref='project', lazy=True, cascade='all, delete-orphan')
    plan_versions = db.relationship('ProjectPlanVersionModel', backref='project', lazy=True, cascade='all, delete-orphan')
    plan_signatures = db.relationship('ProjectPlanSignatureModel', backref='project', lazy=True, cascade='all, delete-orphan')

    plan_version = Column(Integer, default=1, comment='计划版本')
    current_version = Column(Integer, default=1, comment='当前计划版本')

    is_close = Column(Boolean, default=False, comment='是否关闭')

    # 以下字段不在使用
    name = Column(String(50), comment='项目名称')
    # plan_version = Column(Integer, default=1, comment='计划版本')
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
            "isAudited": self.isAudited,
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
            "current_version": self.current_version,
            "designer": self.designer.name if self.designer else "",
            "manager": self.manager.name if self.manager else "",
            "manager_id": self.manager_id,
            "m_designer": self.m_designer.name if self.m_designer else "",
            "e_designer": self.e_designer.name if self.e_designer else "",
            "am_designer": self.am_designer.name if self.am_designer else "",
            "ae_designer": self.ae_designer.name if self.ae_designer else "",
            "creator": self.creator.name if self.manager else "",
            "creator_id": self.creator_id,
            # "plan_version": self.plan_version,
            "plan_version": self.get_max_version(),
            "plan_status": self.get_plan_status()
            # "is_released": self.is_released()
        }

    # 项目信息评审
    def info_audit(self, event):
        """
        实例方法：项目信息的评审
        param event:评审内容（approve=已审核， reject=待提交）
        return 无
        """
        if event == 'approve':
            self.status = '已审核'
        elif event == "reject":
            self.status = "待提交"
        self.save()

    # 查询指定项目的版本信息(获取最大计划版本号)
    def get_version_info(self, project_id):
        """获取项目的版本状态和最大版本号"""
        result = db.session.execute(
            select(
                func.count(ProjectPlanVersionModel.plan_version).label('count'),
                func.max(ProjectPlanVersionModel.plan_version).label('max')
            ).where(ProjectPlanVersionModel.project_id == project_id)
        ).one()

        return {
            "has_version": result.count > 0,
            "max_version": result.max if result.count else None
        }

    def get_max_version(self, is_released=None):
        """
        实例方法：获取当前项目的最大版本号，支持按发布状态筛选
        param is_released: 发布状态筛选（True=已发布，None=全部）
        return：最大版本号（int），无符合条件的版本则返回 0
        """
        # 基础查询：当前项目的版本号最大值
        query = select(func.max(ProjectPlanVersionModel.plan_version)).where(ProjectPlanVersionModel.project_id == self.id)

        # 根据参数添加发布状态筛选条件
        if is_released:
            query = query.where(ProjectPlanVersionModel.is_released == True)

        # 执行查询并返回结果
        result = db.session.execute(query).scalar()
        return result if result else 0

    def is_released(self, version=None):
        """
        实例方法：查询指定计划版本是否发布
        param plan_version： 计划版本，没有传入时为最大版本
        return: 计划版本的发布状态。无相应计划版本时，返回False
        """
        if not version:
            version = self.get_max_version()
        # 确认当前计划版本是否已发布
        q = db.select(ProjectPlanVersionModel).filter(ProjectPlanVersionModel.project_id == self.id,
                                                      ProjectPlanVersionModel.plan_version == version)
        plan_version = db.session.execute(q).scalar()
        if not plan_version:
            return False
        try:
            return plan_version.is_released
        except Exception as e:
            return False

    def get_plan_status(self, version=None):
        """
        实例方法：查询指定计划版本是否发布
        param version： 计划版本，没有传入时为最大版本
        return: 计划版本的发布状态。无相应计划版本时，返回False
        """
        if not version:
            version = self.get_max_version()
        plan_version = ProjectPlanVersionModel.query.filter(
            ProjectPlanVersionModel.project_id == self.id
        ).filter(
            ProjectPlanVersionModel.plan_version == version
        ).first()
        if not plan_version:
            return None
        else:
            return plan_version.status

    # 创建一个新的项目计划版本
    def initial_plan_create(self, version=1):
        # 如果存在该版本的计划，则不允许创建
        plan_version = ProjectPlanVersionModel.query.filter(
            ProjectPlanVersionModel.project_id == self.id
        ).filter(
            ProjectPlanVersionModel.plan_version == version
        ).first()

        if plan_version:
            return False, f'重复项目计划版本，不允许重复创建。'

        try:
            parent_nodes = ProjectNodeTitleModel.query.filter(
                ProjectNodeTitleModel.parent_id.is_(None)
            ).all()

            # 逐个创建父节点及其子节点
            for node in parent_nodes:
                # 创建父节点
                parent_node = ProjectNodeModel(
                    name=node.name,
                    node_id=node.node_id,
                    project_id=self.id,
                    version=version,
                    manager=self.manager
                )
                db.session.add(parent_node)
                db.session.flush()  # 刷新已获取id

                # 创建对应的子节点
                for child_node in node.children:
                    child_node = ProjectNodeModel(
                        parent_id=parent_node.id,
                        name=child_node.name,
                        node_id=child_node.node_id,
                        project_id=self.id,
                        version=version,
                        manager=self.manager
                    )
                    db.session.add(child_node)

            # 创建版本信息
            plan_version = ProjectPlanVersionModel(
                project_id=self.id,
                plan_version=version
            )
            db.session.add(plan_version)
            # 提交事务
            db.session.commit()
            return True, f'项目:{self.customer} 计划创建成功；计划版本：{version}'
        except Exception as e:
            # 事务回滚
            db.session.rollback()
            return False, f'项目:{self.customer} 计划创建失败;{str(e)}'

    # 删除指定计划版本,删除该版本下的所有节点信息
    def plan_delete(self, version):
        nodes = ProjectNodeModel.query.filter(
            ProjectNodeModel.project_id == self.id
        ).filter(
            ProjectNodeModel.version == version
        ).all()
        for node in nodes:
            try:
                db.session.delete(node)
                db.session.commit()
            except Exception as e:
                print(e)

    def add_initial_plan_version(self):
        plan_version = ProjectPlanVersionModel()
        plan_version.project_id = self.id
        plan_version.plan_version = self.plan_version
        plan_version.save()

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
    # delay_days = Column(Integer, comment='拖期天数')

    is_used = Column(Boolean, default=True, comment='是否使用')

    manager_id = Column(Integer, ForeignKey("user.id"))
    manager = db.relationship("UserModel", back_populates="plan_nodes")

    project_id = Column(Integer, ForeignKey("project.id"), nullable=False, comment="所属项目id")

    parent_id = Column(Integer, ForeignKey('project_node.id'), default=None, comment='阶段节点id')
    parent = db.relationship('ProjectNodeModel', back_populates='children', remote_side=[id])
    children = db.relationship('ProjectNodeModel', back_populates='parent', cascade='all, delete-orphan', lazy=True)

    # 不在使用
    owner = Column(String(10), comment='负责人')
    is_close = Column(Boolean, default=False, comment='是否关闭')

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

    # 计算拖期天数
    def calculate_delay_days(self):
        if self.planned_end_date:
            if self.actual_end_date:
                # self.delay_days = (self.actual_end_date - self.planned_end_date).days
                return (self.actual_end_date - self.planned_end_date).days
            else:
                # self.delay_days = (datetime.now() - self.planned_end_date).days
                today = date.today()
                return (today - self.planned_end_date.date()).days if today >= self.planned_end_date.date() else ""
        else:
            return ""

    # 更新父任务
    def update_parent_node(self):
        if self.parent:
            sub_nodes = self.parent.children
            # 更新父任务的计划开始日期为所有子任务中最早的计划开始日期
            if all(node.planned_start_date for node in sub_nodes if node.is_used is True):
                earliest_planned_start = min([node.planned_start_date for node in sub_nodes if node.planned_start_date])
                self.parent.planned_start_date = earliest_planned_start
            else:
                self.parent.planned_start_date = None

            # 更新父任务的计划结束日期为所有子任务中最晚的计划结束日期
            if all(node.planned_end_date for node in sub_nodes if node.is_used is True):
                latest_planned_end = max([node.planned_end_date for node in sub_nodes if node.planned_end_date])
                self.parent.planned_end_date = latest_planned_end
            else:
                self.parent.planned_end_date = None

            # 更新父任务的实际开始日期为所有子任务中最早的实际开始日期
            if all(node.actual_start_date for node in sub_nodes if node.is_used is True):
                earliest_actual_start = min([node.actual_start_date for node in sub_nodes if node.actual_start_date])
                self.parent.actual_start_date = earliest_actual_start
            else:
                self.parent.actual_start_date = None

            # 更新父任务的实际结束日期为所有子任务中最晚的实际结束日期
            if all(node.actual_end_date for node in sub_nodes if node.is_used is True):
                latest_actual_end = max([node.actual_end_date for node in sub_nodes if node.actual_end_date])
                self.parent.actual_end_date = latest_actual_end
            else:
                self.parent.actual_end_date = None

            # 计算父任务的周期
            self.parent.calculate_period()

            db.session.commit()

    # 获取即将拖期的项目（3天）
    @classmethod
    def get_expected_delay(cls, user_id=None):
        """
        查询满足以下条件的节点
        1. 不是父节点
        2. 有计划结束日期
        3. 无实际结束日期
        4. 实际结束日期在今后3天内（包括今天）
        """
        # 获取当天日期
        today = datetime.today().date()
        # 计算3天后的日期
        three_days_later = today + timedelta(days=3)

        # 构建查询
        query = cls.query.filter(
            cls.parent_id != None,
            cls.planned_start_date != None,
            cls.planned_end_date != None
        ).filter(or_(
            and_(
                cls.actual_start_date == None,
                cls.planned_start_date <= three_days_later
            ),
            and_(
                cls.actual_end_date == None,
                cls.planned_end_date <= three_days_later
            )
        )

        )
        if user_id:
            query = query.filter(
                cls.manager_id == user_id
            )
        nodes = query.all()

        result = []
        for node in nodes:
            # 获取该节点所属的项目计划版本，只有状态为【已发布】的节点才将数据返回
            stmt = ProjectPlanVersionModel.query.filter(
                ProjectPlanVersionModel.project_id == node.project_id,
                ProjectPlanVersionModel.plan_version == node.version
            )
            plan_version = db.session.execute(stmt).first()
            if not plan_version or plan_version[0].status != '已发布':
                continue

            node_data = {
                'project': node.project.customer,
                'project_number': node.project.project_number,
                'manager_id': node.manager_id if node.manager_id else "",
                'manager': node.manager.name if node.manager else "",
                'manager_email': node.manager.email if node.manager else "",
                'node_id': node.id,
                'node_name': node.name,
                'planned_start_date': node.planned_start_date.strftime("%Y-%m-%d") if node.planned_start_date else "",
                'planned_end_date': node.planned_end_date.strftime("%Y-%m-%d") if node.planned_end_date else "",
                'actual_start_date': node.actual_start_date.strftime("%Y-%m-%d") if node.actual_start_date else "",
                'days': (node.planned_end_date.date() - today).days
            }
            result.append(node_data)
        return result

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
            "delay_days": self.calculate_delay_days(),
            "owner": self.owner,
            "manager": self.manager.name if self.manager else "",
            "is_used": self.is_used,
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
    # project = db.relationship('ProjectModel')
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
    # project = db.relationship('ProjectModel', backref='plan_versions')
    plan_version = Column(Integer, default=1, comment='计划版本')
    status = Column(String(10), default="待提交", comment='发布状态')
    is_released = Column(Boolean, default=False, comment='已发布')
    release_date = Column(DateTime, comment="发布日期")
    create_at = Column(DateTime, default=datetime.now, comment="创建日期")

    def __repr__(self):
        return "<ProjectPlanVersion %r>" % self.project.customer

    def json(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "project": self.project.customer,
            "plan_version": self.plan_version,
            "status": self.status,
            "is_released": self.is_released,
            "release_date": self.release_date.strftime("%Y-%m-%d") if self.release_date else "",
            "create_at": self.create_at.strftime("%Y-%m-%d") if self.create_at else "",
        }