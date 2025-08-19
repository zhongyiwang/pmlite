from flask import Flask, render_template
from configs import config
from .extensions import register_extensions
from pmlite.apis import register_apis
from pmlite.views import register_views
from pmlite.extensions.email_service import EmailService


def create_app(config_name="prod"):
    app = Flask("pmlite")
    # 新增：关闭 ASCII 编码，确保中文正常显示
    app.config['JSON_AS_ASCII'] = False
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_apis(app)
    register_views(app)

    @app.errorhandler(403)
    def handle_403(e):
        return render_template("error/403.html")

    @app.errorhandler(404)
    def handle_404(e):
        return render_template("error/404.html")

    @app.errorhandler(500)
    def handle_500(e):
        return render_template("error/500.html")

    # 上下文处理函数
    # @app.context_processor
    # def inject_permissions():
    #     return dict(Permission=Permission)

    return app


# __all__ = ["UserModel"]
