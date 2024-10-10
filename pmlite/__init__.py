from flask import Flask, render_template

from configs import config
from .extensions import register_extensions
from pmlite.apis import register_apis
from pmlite.views import register_views
from .models import Permission

# from pmlite.models import UserModel


def create_app(config_name="dev"):
    app = Flask("pmlite")
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
    @app.context_processor
    def inject_permissions():
        return dict(Permission=Permission)

    return app


# __all__ = ["UserModel"]
