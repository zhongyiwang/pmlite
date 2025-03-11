from flask_jwt_extended import JWTManager

from ..models import UserModel

jwt = JWTManager()


# 从用户对象中提取唯一标识符，被用来生产JWT中的identity字段
# 当调用`create_access_token`并传入用户对象时，`flask-jwt-extended`会自动调用这个函数还获取用户标识，并储存在JWT中。
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


# 验证JWT并获取用户信息
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserModel.query.filter(UserModel.id == identity).one_or_none()


@jwt.expired_token_loader
def expired_token_callback():
    print("token 已过期。。。")
    return {"msg": "token 已过期，请重新登录", "code": -1}, 403


@jwt.unauthorized_loader
def missing_token_callback(error):
    print("非登录用户请求。")
    return {"msg": "未登录用户，请登录后重试！", "code": -1}
