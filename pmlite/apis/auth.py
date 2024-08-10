from flask import Blueprint, request, make_response

from flask_jwt_extended import create_access_token, create_refresh_token, get_current_user, jwt_required

from pmlite.extensions import db
from pmlite.models import UserModel


auth_api = Blueprint("auth", __name__)


# 登录
@auth_api.post("/login")
def login_in():
    data = request.get_json()

    user: UserModel = db.session.execute(
        db.select(UserModel).where(UserModel.number == data["number"])
    ).scalar()

    if not user:
        return {"msg": "用户不存在", "code": -1}
    if not user.check_password(data["password"]):
        return {"msg": "用户密码错误", "code": -1}

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    response = make_response(
        {
            "code": 0,
            "msg": "登录成功",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )
    return response


# 退出登录
@auth_api.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return {"msg": "退出登录成功!", "code": 0}