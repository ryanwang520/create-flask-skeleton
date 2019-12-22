from flask import Blueprint, request

from ..auth import check_auth, encode_jwt
from ..api import dataschema
from ..models import User

bp = Blueprint("admin", __name__, url_prefix="/admin")

AUD_ADMIN = "AUD_ADMIN"


@bp.before_request
def before_request():
    if not request.endpoint.endswith("login"):
        check_auth(audience=AUD_ADMIN)


@bp.route("/users")
def users():
    users = User.query.offset(0).limit(10)

    def serialize(user):
        return {"id": user.id, "name": user.name}

    return [serialize(user) for user in users]


@bp.route("/login", methods=["POST"])
@dataschema({"name": str})
def login(name):
    user = User.query.filter_by(name=name).one()
    token = encode_jwt({"id": user.id}, AUD_ADMIN)
    return {"token": token.decode("utf-8"), "user": {"name": user.name, "id": user.id}}
