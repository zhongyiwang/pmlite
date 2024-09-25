from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required

from pmlite.models import SupplierModel
from ..extensions import db


supplier_api = Blueprint("supplier", __name__, url_prefix="/supplier")


# 获取列表
@supplier_api.route('/')
def user_view():
    users = db.session.execute(db.select(SupplierModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(users),
        'data': [user.json() for user in users]
    }


# 获取用户列表，分页显示
@supplier_api.route('/pagination')
def supplier_view_pagination():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=10)
    q = db.select(SupplierModel)

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


# 添加
@supplier_api.post('/')
def supplier_add():
    data = request.get_json()
    supplier = SupplierModel()
    supplier.update(data)
    try:
        supplier.save()
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


# 修改
@supplier_api.put('/<int:sid>')
def supplier_edit(sid):
    data = request.get_json()
    supplier = db.get_or_404(SupplierModel, sid)
    supplier.update(data)
    try:
        supplier.save()
    except Exception as e:
        print(e)
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


# 删除
@supplier_api.delete('/<int:sid>')
def supplier_delete(sid):
    supplier: SupplierModel = db.get_or_404(SupplierModel, sid)
    try:
        # db.session.delete(supplier)
        supplier.disabled = True
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
