import importlib
import os
import yaml
import logging
import traceback
from flask import request

from .api import ApiException, ApiFlask
from .globals import db, migrate
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from werkzeug.routing import RequestRedirect
from werkzeug.utils import redirect


def create_app(config=None):
    config = config or {}
    app = ApiFlask('{{ app }}')
    config_path = os.environ['APP_SETTINGS']
    with open(config_path) as f:
        config.update(yaml.load(f))
    app.config.update(config)

    register_blueprints(app)
    db.init_app(app)
    migrate.init_app(app)
    init_shell(app)

    register_error_handlers(app)
    return app


def create_api_app():
    pass


def create_normal_app():
    pass


def register_blueprints(app):
    from .apps.admin import bp as admin
    app.register_blueprint(admin)
    from .apps.user import bp as user
    app.register_blueprint(user)


def register_error_handlers(app):
    def wants_json_response():
        return (
                request.accept_mimetypes["application/json"]
                >= request.accept_mimetypes["text/html"]
        )

    app.register_error_handler(ApiException, lambda err: err.to_result())

    logger = logging.getLogger(__name__)

    def handle_err(e):
        if wants_json_response():
            if isinstance(e, BadRequest):
                return ApiException(e.description).to_result()
            if isinstance(e, NotFound):
                return ApiException("Not Found", status=404).to_result()
            if isinstance(e, MethodNotAllowed):
                return ApiException("method not allowed", status=405).to_result()
            logger.exception("系统异常")
            if app.debug:
                return ApiException(traceback.format_exc(), status=500).to_result()
            return ApiException("系统异常", status=500).to_result()
        if isinstance(e, NotFound):
            return "resource not found", 404
        if isinstance(e, MethodNotAllowed):
            return "method not allowed", 405
        if isinstance(e, RequestRedirect):
            return redirect(e.new_url)
        raise e

    app.register_error_handler(Exception, handle_err)

    app.register_error_handler(ApiException, lambda err: err.to_result())


def init_shell(app):
    @app.cli.command("ishell")
    def shell():
        # lazy import these modules as they are only used in the shell context
        from IPython import embed, InteractiveShell
        import cProfile
        import pdb

        main = importlib.import_module("__main__")

        banner = f"App: poi"
        from . import models

        ctx = main.__dict__
        ctx.update(
            {
                **models.__dict__,
                "session": db.session,
                "pdb": pdb,
                "cProfile": cProfile,
            }
        )

        with app.app_context():
            ctx.update(app.make_shell_context())
            InteractiveShell.colors = "Neutral"
            embed(user_ns=ctx, banner2=banner)
