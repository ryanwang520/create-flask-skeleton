import jwt
from flask import Blueprint, current_app

from {{ app }}.api import dataschema
from {{ app }}.auth import requires_auth, ALGORITHMS
from {{ app }}.consts import AUD_APP
from {{ app }}.models import User
from {{ app }}.auth import current_user

bp = Blueprint('{{ app }}', __name__)


@bp.route('/')
def index():
    users = list(User.query.all())
    print(bool(users))
    print(users)
    return 'flask app with sqlalchemy {}'.format("<br/>".join(_.name for _ in users))


@bp.route('/login', methods=['POST'])
@dataschema({
    'name': str,
})
def login(name):
    user = User.query.filter_by(name=name).one()
    token = jwt.encode({'id': user.id, 'aud': AUD_APP},
                       current_app.secret_key,
                       algorithm=ALGORITHMS[0])
    return {
        'token': token.decode('utf-8'),
        'user': {
            'name': user.name,
            'id': user.id,
        }
    }


@bp.route('/profile')
@requires_auth(AUD_APP)
def profile():
    return 'this is profile of {}'.format(current_user.name)


@bp.route('/test', methods=['POST'])
@dataschema({
    'a': int
})
def test(a):
    return {'a': a}