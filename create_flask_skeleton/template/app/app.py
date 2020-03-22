import importlib
import os
from yaml import load
from yaml import CLoader as Loader

import logging
import traceback
from flask import request

from .api import ApiException, ApiFlask
from .globals import db, migrate
from .cors import append_cors_header
from werkzeug.exceptions import HTTPException


def create_app(config=None):
    config = config or {}
    app = ApiFlask("{{ app }}")
    config_path = os.environ.get("APP_SETTINGS", "config.yaml")
    with open(config_path) as f:
        config.update(load(f, Loader=Loader))
    app.config.update(config)

    app.after_request(append_cors_header)

    register_blueprints(app)
    db.init_app(app)
    migrate.init_app(app, db)
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
        if isinstance(e, HTTPException):
            return e
        if wants_json_response():
            logger.exception("系统异常")
            if app.debug:
                return ApiException(traceback.format_exc(), status=500).to_result()
            return ApiException("系统异常", status=500).to_result()
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
