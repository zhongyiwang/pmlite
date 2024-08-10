import os
from datetime import timedelta


# 设置session过期时间，不设置的话，默认为31天。
# PERMANENT_SESSION_LIFETTIME = timedelta(days=7)

class BaseConfig:
    # 密钥
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    SQLALCHEMY_DATABASE_URI = ""

    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)


class DevelopmentConfig(BaseConfig):
    # 开发配置
    SQLALCHEMY_DATABASE_URI = "sqlite:///pmlite.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(BaseConfig):
    """测试配置"""
    # 内存数据库
    QLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    """生产环境配置"""
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@127.0.0.1:3306/pmlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {"dev": DevelopmentConfig, "test": TestingConfig, "prod": ProductionConfig}
