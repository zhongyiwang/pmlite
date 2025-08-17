import os
from datetime import timedelta
from dotenv import load_dotenv

# 设置session过期时间，不设置的话，默认为31天。
# PERMANENT_SESSION_LIFETTIME = timedelta(days=7)

load_dotenv()

class BaseConfig:

    # 密钥
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    SQLALCHEMY_DATABASE_URI = ""

    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

    # JWT配置项目
    # 指定查找JWT的位置，默认是headers，也可以是cookies等，放在列表中。
    # JWT_TOKEN_LOCATION = ["headers"]
    # JWT访问令牌的有效期
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = (os.environ.get('MAIL_DEFAULT_SENDER_NAME'), os.environ.get('MAIL_USERNAME'))


class DevelopmentConfig(BaseConfig):
    # 开发配置
    # SQLALCHEMY_DATABASE_URI = "sqlite:///pmlite.db"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/pmlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(BaseConfig):
    """测试配置"""
    # 内存数据库
    QLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    """生产环境配置"""
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:lnmazak@127.0.0.1:3306/pmlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {"dev": DevelopmentConfig, "test": TestingConfig, "prod": ProductionConfig}
# print('USERNAME', os.getenv("MAIL_USERNAME"))
# print('PASSWORD', os.getenv("MAIL_PASSWORD"))
# print('MAIL_DEFAULT_SENDER', os.getenv("MAIL_DEFAULT_SENDER"))
