from flask import Blueprint, request

from pmlite.extensions import db
from pmlite. models import DepartmentModel

department_api = Blueprint("department", __name__, url_prefix="/department")


# 获取部门列表
@department_api.route('/')
def department_view():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('limit', type=int, default=10)
    q = db.select(DepartmentModel)

    pages: DepartmentModel = db.paginate(q, page=page, per_page=per_page)
    print(type(pages))

    # paginate = DepartmentModel.query.filter_by(is_parent=True).paginate(page=page, per_page=per_page, error_out=False)
    # items = paginate.items
    # items: [DepartmentModel] = paginate.items
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': pages.total,
        'data': [item.json() for item in pages.items]
    }


# 获取部门列表，以树状表格显示
@department_api.get("/treetable")
def department_list_as_treetable():
    # q = db.select(DepartmentModel)
    # q = q.where(DepartmentModel.parent_id == 2)
    # department_list = db.session.execute(q).scalars()

    department_list = db.session.execute(db.select(DepartmentModel).filter(DepartmentModel.parent_id == None)).scalars().all()

    ret = []
    for child in department_list:
        child_data = child.json()
        child_data["children"] = []
        if child.children:
            child_data["isParent"] = True
        for son in child.children:
            son_data = son.json()
            child_data['children'].append(son_data)
        ret.append(child_data)
    return {
        "code": 0,
        "message": "数据请求成功！",
        "data": ret
    }


# 添加部门
@department_api.post('/')
def department_add():
    data = request.get_json()
    department = DepartmentModel()
    department.update(data)
    try:
        department.save()
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
@department_api.put('/<int:uid>')
def department_edit(uid):
    data = request.get_json()
    department = db.get_or_404(DepartmentModel, uid)
    department.update(data)
    try:
        department.save()
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
@department_api.delete('/<int:uid>')
def department_delete(uid):
    department: DepartmentModel = db.get_or_404(DepartmentModel, uid)
    try:
        db.session.delete(department)
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
