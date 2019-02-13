from flask import request, current_app

import jwt
from .api import NotAuthorized, InvalidToken, AuthExpired


JWT_ALGORITHM = "HS256"


def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise NotAuthorized("Authorization header is expected")

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise NotAuthorized("Authorization header must start with bearer")
    elif len(parts) == 1:
        raise NotAuthorized("Token not found")
    elif len(parts) > 2:
        raise NotAuthorized("Authorization header must be" " Bearer token")

    return parts[1]


def check_auth(audience, auth_callback=None):
    token = get_token_auth_header()
    try:
        # different app should not share token
        payload = decode_jwt(token, audience)
    except jwt.ExpiredSignatureError:
        raise AuthExpired("token is expired")
    except jwt.MissingRequiredClaimError:
        raise NotAuthorized("incorrect claims, please check the audience and issuer")
    except jwt.InvalidIssuerError:
        raise InvalidToken("issuer invalid")
    except jwt.InvalidAudience:
        raise InvalidToken("audience invalid")
    except jwt.InvalidTokenError:
        raise InvalidToken("Unable to parse authentication header")
    except jwt.InvalidSignatureError:
        raise InvalidToken("token secret not match")

    if auth_callback:
        auth_callback(payload)


def decode_jwt(token, audience):
    return jwt.decode(
        token.encode("utf-8"),
        current_app.secret_key,
        algorithms=JWT_ALGORITHM,
        audience=audience,
    )


def encode_jwt(payload, audience):
    return jwt.encode({**payload, "aud": audience}, current_app.secret_key)
