import csv
import os
from datetime import datetime

from flask import Flask, current_app

from ..extensions import db
from ..models import UserModel, DepartmentModel, MachineTypeModel, ProjectModel, TaskTypeModel, TaskModel, ManHourModel, ProjectNodeTitleModel, MachiningProcessModel, RoleModel, PermissionModel


def is_valid_date(date_str):
    date_format = "%Y-%m-%d"
    try:
         return datetime.strptime(date_str, date_format)

    except ValueError:
        return False


def dict_to_model(d, m):
    for k, v in d.items():
        if k == "password":
            m.password = v

        if k in ['is_delay', 'is_automation', 'turn_key']:
            setattr(m, k, bool(int(v)))
        else:
            if v and is_valid_date(v):
                # m.k = is_valid_date(v)
                setattr(m, k, is_valid_date(v))
            else:
                setattr(m, k, v or None)


def csv_to_database(path, model):
    with open(path, encoding="utf-8") as file:
        for d in csv.DictReader(file):
            m = model()
            dict_to_model(d, m)
            db.session.add(m)
            db.session.flush()
        db.session.commit()


def register_script(app: Flask):
    @app.cli.command()
    def init():
        """
        flask初始化
        """
        db.drop_all()
        db.create_all()
        root = current_app.config.get("ROOT_PATH")
        department_data_path = os.path.join(root, "pmlite", "static", "data", "department.csv")
        csv_to_database(department_data_path, DepartmentModel)
        user_data_path = os.path.join(root, "pmlite", "static", "data", "user.csv")
        csv_to_database(user_data_path, UserModel)

        # 机型表
        machine_data_path = os.path.join(root, "pmlite", "static", "data", "machine.csv")
        csv_to_database(machine_data_path, MachineTypeModel)
        # 项目表
        project_data_path = os.path.join(root, "pmlite", "static", "data", "project.csv")
        csv_to_database(project_data_path, ProjectModel)
        # 任务类型表
        task_type_data_path = os.path.join(root, "pmlite", "static", "data", "task_type.csv")
        csv_to_database(task_type_data_path, TaskTypeModel)
        # 任务表
        task_data_path = os.path.join(root, "pmlite", "static", "data", "task.csv")
        csv_to_database(task_data_path, TaskModel)
        # 工时表
        man_hour_data_path = os.path.join(root, "pmlite", "static", "data", "man_hour.csv")
        csv_to_database(man_hour_data_path, ManHourModel)

    @app.cli.command("import_project_node_title")
    def import_project_node_title():
        """
        从csv文件中导入项目的节点标题数据
        """
        root = current_app.config.get("ROOT_PATH")
        project_node_title_data_path = os.path.join(root, "pmlite", "static", "data", "project_node_title.csv")
        csv_to_database(project_node_title_data_path, ProjectNodeTitleModel)

    @app.cli.command("import_machining_process")
    def import_machining_process():
        """
        从csv文件中导入25年的工艺方案
        """
        root = current_app.config.get("ROOT_PATH")
        machining_process_data_path = os.path.join(root, "pmlite", "static", "data", "machining_process.csv")
        csv_to_database(machining_process_data_path, MachiningProcessModel)

    @app.cli.command("import-role-and-pemission")
    def import_machining_process():
        """
        从csv文件中导入角色和权限-20250701
        """
        root = current_app.config.get("ROOT_PATH")
        # 任务表
        role_data_path = os.path.join(root, "pmlite", "static", "data", "role.csv")
        csv_to_database(role_data_path, RoleModel)
        # 权限表
        permission_data_path = os.path.join(root, "pmlite", "static", "data", "permission.csv")
        csv_to_database(permission_data_path, PermissionModel)

    @app.cli.command("set-system-admin")
    def import_machining_process():
        """
        设置10028为系统管理员
        """
        user = UserModel.query.filter_by(number=10028).first()
        role = RoleModel.query.filter_by(name='system_admin').first()
        if user and role:
            user.role = role
            db.session.add(user)
            db.commit()
