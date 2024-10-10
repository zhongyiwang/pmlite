from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required

from pmlite.models import UserModel
from ..extensions import db


user_api = Blueprint("user", __name__, url_prefix="/user")


# 获取用户列表
@user_api.route('/')
def user_view():
    users = db.session.execute(db.select(UserModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(users),
        'data': [user.json() for user in users]
    }


# 获取用户列表，分页显示
@user_api.route('/pagination')
def user_view_pagination():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=10)
    q = db.select(UserModel)

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    # paginate = UserModel.query.paginate(page=page, per_page=per_page, error_out=False)
    # items = paginate.items
    # items: [UserModel] = paginate.items
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': pages.total,
        'data': [item.json() for item in pages.items]
    }


# 添加用户
@user_api.post('/')
def user_add():
    data = request.get_json()
    user = UserModel()
    user.update(data)
    user.password = "123456"
    try:
        user.save()
    except Exception as e:
        print(e)
        return {
            'code': -1,
            'msg': '新增数据失败'
        }
    return {
        'code': 0,
        'msg': '新增数据成功'
    }


# 修改用户数据
@user_api.put('/<int:uid>')
def user_edit(uid):
    data = request.get_json()
    print(data)
    # user = StudentORM.query.get(uid)
    user = db.get_or_404(UserModel, uid)
    user.update(data)
    try:
        user.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


# 删除用户
@user_api.delete('/<int:uid>')
def user_delete(uid):
    user: UserModel = db.get_or_404(UserModel, uid)
    try:
        db.session.delete(user)
        # user.is_del = True
        db.session.commit()
    except Exception as e:
        return {
            'code': -1,
            'msg': '删除数据失败'
        }
    return {
        'code': 0,
        'msg': '删除数据成功'
    }


# 获取用户信息
@user_api.get("/profile")
@jwt_required()
def user_profile():
    return {
        "code": 0,
        "msg": "获取个人数据成功！",
        "data": current_user.json(),
        'permissions': current_user.role.permissions if current_user.role else ""
    }


