from datetime import datetime
from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import desc, or_
from flask_jwt_extended import current_user, jwt_required

from pmlite.models import MachiningProcessModel, MachiningProcessStatusModel, WorkShapeModel, CustomerIndustryModel, ProjectTypeModel, UserModel
from ..extensions import db


machining_process_api = Blueprint("machining_process", __name__, url_prefix="/machining_process")


# 获取列表(工艺方案）
@machining_process_api.route('/')
def mp_view():
    projects = db.session.execute(db.select(MachiningProcessModel)).scalars().all()
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': len(projects),
        'data': [user.json() for user in projects]
    }


# 获取列表，分页显示
@machining_process_api.route('/pagination')
@jwt_required()
def view_pagination():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=10)

    # 自定义查询字符串
    show_all = request.args.get('showAll')
    customer = request.args.get('customer')
    manager_name = request.args.get('manager')
    sales_manager = request.args.get('sales_manager')
    mine = request.args.get('mine')

    q = db.select(MachiningProcessModel).order_by(desc(MachiningProcessModel.id))


    # if not show_all:  # 默认获取未完成项目
    #     q = q.filter(MachiningProcessModel.is_close.isnot(True))

    if customer:  # 外部查询，模糊查询客户字段
        page = 1  # 避免在选择分页后查询报警，查询默认显示第1页数据
        q = q.filter(MachiningProcessModel.customer.like('%' + customer + '%'))

    if sales_manager:  # 外部查询，模糊查询客户字段
        page = 1  # 避免在选择分页后查询报警，查询默认显示第1页数据
        q = q.filter(MachiningProcessModel.sales_manager.like('%' + sales_manager + '%'))

    if manager_name:
        page = 1
        user_id = UserModel.query.filter_by(name=manager_name).first().id
        q = q.filter(MachiningProcessModel.manager_id == user_id)

    if mine:
        q = q.filter(MachiningProcessModel.manager_id == current_user.id)

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': pages.total,
        'data': [item.json() for item in pages.items]
    }

# 添加（工艺方案）
@machining_process_api.post('/')
def mp_add():
    data = request.get_json()
    mp = MachiningProcessModel()
    mp.update(data)
    try:
        mp.save()
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
@machining_process_api.put('/<int:mp_id>')
def mp_edit(mp_id):
    data = request.get_json()
    # print(data)
    # user = StudentORM.query.get(uid)
    mp = db.get_or_404(MachiningProcessModel, mp_id)
    mp.update(data)
    try:
        mp.save()
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
@machining_process_api.delete('/<int:mp_id>')
def mp_delete(mp_id):
    mp: MachiningProcessModel = db.get_or_404(MachiningProcessModel, mp_id)
    try:
        db.session.delete(mp)
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


# 修改当月的项目状态
@machining_process_api.post('/status/<int:_id>')
def update_status(_id):
    now = datetime.now()
    year = now.year
    month = now.month
    data = request.get_json()
    item = db.session.execute(db.select(MachiningProcessStatusModel).where(MachiningProcessStatusModel.project_id == _id,
                                                                           MachiningProcessStatusModel.year == year,
                                                                           MachiningProcessStatusModel.month == month)).scalar()
    if item:
        item.update({
            'status': data['this_month']
        })
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
    else:
        item = MachiningProcessStatusModel()
        item.update({
            'year': year,
            'month': month,
            'project_id': _id,
            'status': data['this_month']
        })
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