from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from flask_jwt_extended import current_user, jwt_required

from pmlite.models import CustomerIndustryModel
from ..extensions import db


customer_industry_api = Blueprint("customer_industry", __name__, url_prefix="/customer_industry")


# 获取列表
@customer_industry_api.route('/')
def listview():
    items = db.session.execute(db.select(CustomerIndustryModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(items),
        'data': [item.json() for item in items]
    }


# 添加
@customer_industry_api.post('/')
def mp_add():
    data = request.get_json()
    item = CustomerIndustryModel()
    item.update(data)
    try:
        item.save()
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
@customer_industry_api.put('/<int:_id>')
def edit(_id):
    data = request.get_json()
    # print(data)
    # user = StudentORM.query.get(uid)
    item = db.get_or_404(CustomerIndustryModel, _id)
    item.update(data)
    try:
        item.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': '修改数据失败'
        }
    return {
        'code': 0,
        'msg': '修改数据成功'
    }


# 删除
@customer_industry_api.delete('/<int:_id>')
def delete(_id):
    item: CustomerIndustryModel = db.get_or_404(CustomerIndustryModel, _id)
    try:
        db.session.delete(item)
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


# 返回drowpdown的data数据
@customer_industry_api.get('/dropdown')
def dropdown():
    items = db.session.execute(db.select(CustomerIndustryModel)).scalars().all()
    ret = []
    _id = 100
    for item in items:
        title = item.name
        data = {
            "title": title,
            "id": _id
        }
        ret.append(data)
        _id += 1
    return ret
