from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from pmlite.extensions import db
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
# from .project import project_user_table

from ._base import BaseModel
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
    default = Column(Boolean, default=False, comment='默认角色')
    # permissions = Column(Integer, comment='权限')
    permissions = db.relationship('PermissionModel', secondary='role_permission',
                                  backref=db.backref('roles', lazy='dynamic'))

    users = db.relationship('UserModel', backref='role', lazy='dynamic')

    # @staticmethod
    # def insert
    #     roles = {
    #         'Designer': [Permission.PROJECT, Permission.TASK],
    #         'Quoter': [Permission.PROJECT, Permission.TASK, Permission.PRICE],
    #         "Admin": [Permission.PROJECT, Permission.TASK, Permission.PRICE, Permission.ADMIN],
    #     }
    #     default_role = 'Designer'
    #     for r in roles:
    #         q = db.select(RoleModel).where(RoleModel.name == r)
    #         role = db.session.execute(q).scalar()
    #         if role is None:
    #             role = RoleModel(name=r)
    #         role.reset_permission()
    #         for perm in roles[r]:
    #             role.add_permission(perm)
    #         role.default = (role.name == default_role)
    #         db.session.add(role)
    #     db.session.commit()_roles():

    def __repr__(self):
        return '<Role %r>' % self.name

    def json(self):
        return {
            'id': self.id,
            'name': self.name
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


# class Permission:
#     PROJECT = 1
#     TASK = 2
#     PRICE = 4
#     ADMIN = 16
