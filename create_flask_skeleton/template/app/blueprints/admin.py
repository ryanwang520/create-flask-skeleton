import jwt
from flask import Blueprint, current_app, request

from {{ app }}.api import dataschema
from {{ app }}.auth import check_auth, ALGORITHMS
from {{ app }}.consts import AUD_ADMIN
from {{ app }}.models import User

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.before_request
def before_request():
    if not request.endpoint.endswith('login'):
        check_auth(audience=AUD_ADMIN)


@bp.route('/users')
def users():
    users = User.query.offset(0).limit(10)

    def serialize(user):
        return {
            'id': user.id,
            'name': user.name
        }

    return [serialize(user) for user in users]


@bp.route('/login', methods=['POST'])
@dataschema({
    'name': str,
})
def login(name):
    user = User.query.filter_by(name=name).one()
    token = jwt.encode({'id': user.id, 'aud': AUD_ADMIN},
                       current_app.secret_key,
                       algorithm=ALGORITHMS[0])
    return {
        'token': token.decode('utf-8'),
        'user': {
            'name': user.name,
            'id': user.id,
        }
    }
