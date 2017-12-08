import functools

import jwt
import lazy_object_proxy

from flask import request, _app_ctx_stack, current_app
from flask.globals import _app_ctx_err_msg
from werkzeug.local import LocalProxy

from .consts import AUD_APP
from .models import User
from .api import ApiException


class AuthError(ApiException):
    status = 401


AUTH0_DOMAIN = 'YOUR_AUTH0_DOMAIN'
API_AUDIENCE = 'GUANMENWANG'
# ALGORITHMS = ["RS256"]
ALGORITHMS = ["HS256"]


def _lookup_current_user():
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError(_app_ctx_err_msg)
    return getattr(top, 'current_user', None)


current_user = LocalProxy(_lookup_current_user)


def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                             "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must start with"
                             " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Authorization header must be"
                             " Bearer token"}, 401)

    return parts[1]


def check_auth(audience=AUD_APP):
    token = get_token_auth_header()
    try:
        # different app should not share token
        payload = jwt.decode(
            token.encode('utf-8'),
            current_app.secret_key,
            algorithms=ALGORITHMS,
            audience=audience
        )
    except jwt.ExpiredSignatureError:
        raise AuthError({"code": "token_expired",
                         "description": "token is expired"}, 401)
    except jwt.MissingRequiredClaimError:
        raise AuthError({"code": "invalid_claims",
                         "description":
                             "incorrect claims,"
                             "please check the audience and issuer"}, 401)
    except jwt.InvalidIssuerError:
        raise AuthError('issuer invalid')
    except jwt.InvalidAudience:
        raise AuthError('audience invalid')
    except jwt.InvalidTokenError:
        raise AuthError({"code": "invalid_header",
                         "description":
                             "Unable to parse authentication"
                             " token."}, 400)

    user_id = payload['id']

    user = lazy_object_proxy.Proxy(lambda: User.query.filter_by(id=user_id).first())
    _app_ctx_stack.top.current_user = user


def check_auth_by_aud(func, audience):
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        check_auth(audience)
        return func(*args, **kwargs)

    return decorated


def requires_auth(f):
    """Determines if the access token is valid
    """

    if isinstance(f, str):

        def inner(func):
            return check_auth_by_aud(func, f)

        return inner

    else:
        return check_auth_by_aud(f, AUD_APP)
