import functools

from flask import Blueprint, g

from ..auth import check_auth, encode_jwt
from ..api import dataschema
from ..models import User
from ..globals import current_user

bp = Blueprint("{{ app }}", __name__)


@bp.route("/")
def index():
    return "welcome to flask world!"


@bp.route("/db")
def db():
    users = list(User.query.all())
    return "flask app with sqlalchemy {}".format("<br/>".join(_.name for _ in users))


@bp.route("/login", methods=["POST"])
@dataschema({"name": str})
def login(name):
    user = User.query.filter_by(name=name).one()
    token = encode_jwt({"id": user.id}, "AUD_APP")
    return {"token": token.decode("utf-8"), "user": {"name": user.name, "id": user.id}}


def auth_callback(payload):
    user_id = payload["id"]
    g.user = User.find_one(User.id == user_id)


def login_required(fn):
    functools.wraps(fn)

    def wrapper(*args, **kwargs):
        check_auth("AUD_APP", auth_callback)
        return fn(*args, **kwargs)

    return wrapper


@bp.route("/profile")
@login_required
def profile():
    return "this is profile of {}".format(current_user().name)


@bp.route("/test", methods=["POST"])
@dataschema({"a": int})
def test(a):
    return {"a": a}
