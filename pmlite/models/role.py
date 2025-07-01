from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from pmlite.extensions import db
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.exc import IntegrityError
# from .project import project_user_table

from ._base import BaseModel
from ..models import UserModel
from .task import user_task


role_permission = db.Table('role_permission',
                           Column('role_id', Integer, ForeignKey('role.id')),
                           Column('permission_id', Integer, ForeignKey('permission.id'))
                           )


class RoleModel(BaseModel):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    name = Column(String(64), unique=True, comment='角色名称')
    desc = Column(String(64), comment='角色描述')
    # default = Column(Boolean, default=False, comment='默认角色')
    # permissions = Column(Integer, comment='权限')
    permissions = db.relationship('PermissionModel', secondary='role_permission',
                                  backref=db.backref('roles', lazy='dynamic'))

    # users = db.relationship('UserModel', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    def add_permission(self, permission_id):
        """添加单个权限到角色"""
        permission = PermissionModel.query.get(permission_id)
        if permission and permission not in self.permissions:
            self.permissions.append(permission)
            try:
                db.session.commit()
                return True, "权限添加成功"
            except IntegrityError:
                db.session.rollback()
                return False, "数据库错误，添加失败"
        return False, "权限不存在或已分配"

    def add_permissions(self, permission_ids):
        """批量添加权限到角色"""
        success = True
        message = []
        for pid in permission_ids:
            result, msg = self.add_permission(pid)
            if not result:
                success = False
                message.append(f"权限ID {pid}： {msg}")
        return success, message if message else "批量权限添加成功"

    def remove_permission(self, permission_id):
        """从角色中移除单个权限"""
        permission = PermissionModel.query.get(permission_id)
        if permission and permission in self.permissions:
            self.permissions.remove(permission)
            try:
                db.session.commit()
                return True, "权限移除成功"
            except IntegrityError:
                db.session.rollback()
                return False, "数据库错误，移除失败"
        return False, "权限不存在或未分配"

    def remove_permissions(self, permission_ids):
        """批量移除角色权限"""
        success = True
        message = []
        for pid in permission_ids:
            result, msg = self.remove_permission(pid)
            if not result:
                success = False
                message.append(f"权限ID {pid}: {msg}")
        return success, message if message else "批量权限移除成功"

    def add_user(self, user_id):
        """给角色添加单个用户"""
        user = UserModel.query.get(user_id)
        if user and not user.role and user not in self.users:
            self.users.append(user)
            try:
                db.session.commit()
                return True, "用户添加成功"
            except IntegrityError:
                db.session.rollback()
                return False, "数据库错误，添加失败"
        return False, "用户不存在或已分配"

    def add_users(self, user_ids):
        """批量给角色添加用户"""
        success = True
        message = []
        for uid in user_ids:
            result, msg = self.add_user(uid)
            if not result:
                success = False
                message.append(f"用户ID {uid}： {msg}")
        return success, message if message else "批量用户添加成功"

    def remove_user(self, user_id):
        """从角色中移除单个用户"""
        user = UserModel.query.get(user_id)
        if user and user in self.users:
            self.users.remove(user)
            try:
                db.session.commit()
                return True, "用户移除成功"
            except IntegrityError:
                db.session.rollback()
                return False, "数据库错误，移除失败"
        return False, "用户不存在或未分配"

    def remove_users(self, user_ids):
        """批量移除角色用户"""
        success = True
        message = []
        for uid in user_ids:
            result, msg = self.remove_user(uid)
            if not result:
                success = False
                message.append(f"权限ID {uid}: {msg}")
        return success, message if message else "批量用户移除成功"


    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'desc': self.desc,
            'users': [item.id for item in self.users],
            'permissions': [item.id for item in self.permissions]
        }

    # def add_permission(self, perm):
    #     if not self.has_permission(perm):
    #         self.permissions += perm

    # def remove_permission(self, perm):
    #     if self.has_permission(perm):
    #         self.permissions -= perm

    # def reset_permission(self):
    #     self.permissions = 0

    # def has_permission(self, perm):
    #     return self.permissions & perm == perm


class PermissionModel(BaseModel):
    __tablename__ = 'permission'
    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增id")
    name = Column(String(64), unique=True, comment='权限名称')
    desc = Column(String(64), comment='权限描述')

    def __repr__(self):
        return '<Permission %r>' % self.name

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'desc': self.desc
        }

# class Permission:
#     PROJECT = 1
#     TASK = 2
#     PRICE = 4
#     ADMIN = 16
