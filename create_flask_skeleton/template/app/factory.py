import os
import yaml
from werkzeug.utils import find_modules, import_string

from . import models
from .models import session
from .api import ApiException, ApiFlask


def create_app(config=None):
    config = config or {}
    app = ApiFlask('{{ app }}')
    config_path = os.environ['APP_SETTINGS']
    with open(config_path) as f:
        config.update(yaml.load(f))
    app.config.update(config)

    models.init_app(app)

    register_blueprints(app)

    register_commands(app)
    register_teardowns(app)
    register_error_handlers(app)
    return app


def register_error_handlers(app):
    app.register_error_handler(ApiException, lambda err: err.to_result())


def create_api_app():
    pass


def create_normal_app():
    pass


def register_blueprints(app):
    """Register all blueprint modules

    Reference: Armin Ronacher, "Flask for Fun and for Profit" PyBay 2016.
    """
    for name in find_modules('{{ app }}.blueprints'):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)
    return None


def register_commands(app):
    @app.cli.command('initdb')
    def initdb():
        return models.init_db(app)


def register_teardowns(app):
    @app.teardown_appcontext
    def close_db(_):
        session.remove()
