import functools

from flask import Response, Flask, json, request
from flask_sqlalchemy import Pagination
from typing import Optional, List

from mypy_extensions import TypedDict
from voluptuous import Schema, Invalid


class ApiResult:
    def __init__(self, value, status=200, next_page=None):
        self.value = value
        self.status = status
        self.nex_page = next_page

    def to_response(self):
        return Response(
            json.dumps(self.value, ensure_ascii=False),
            status=self.status,
            mimetype="application/json",
        )


class ErrorDict(TypedDict):
    message: str
    code: int


class ApiException(Exception):
    code: Optional[int] = None
    message: Optional[str] = None
    errors: Optional[List[ErrorDict]] = None

    status = 400

    def __init__(self, message, status=None, code=None, errors=None):
        self.message = message or self.message
        self.status = status or self.status
        self.code = code or self.code
        self.errors = errors or self.errors

    def to_result(self):
        rv = {"message": self.message}
        if self.errors:
            rv["errors"] = self.errors
        if self.code:
            rv["code"] = self.code
        return ApiResult(rv, status=self.status)


class NotAuthorized(ApiException):
    status = 401


class NotFound(ApiException):
    status = 404
    message = "resource not found"


class InvalidToken(ApiException):
    pass


class AuthExpired(ApiException):
    pass


class ApiFlask(Flask):
    def make_response(self, rv):
        if rv is None:
            rv = {}
        if isinstance(rv, Pagination):
            rv = {
                "pages": rv.pages,
                "has_prev": rv.has_prev,
                "has_next": rv.has_next,
                "total": rv.total,
                "items": rv.items,
            }
        from .globals import db

        if isinstance(rv, db.Model):
            rv = rv.as_dict()
        if isinstance(rv, (dict, list)):
            rv = ApiResult(rv)
        if isinstance(rv, ApiResult):
            response = rv.to_response()
        else:
            response = super(ApiFlask, self).make_response(rv)
        return response


def dataschema(schema):
    if isinstance(schema, dict):
        schema = Schema(schema)

    def decorator(f):
        @functools.wraps(f)
        def new_func(*args, **kwargs):
            try:
                kwargs.update(schema(request.get_json()))
            except Invalid as e:
                raise ApiException(
                    'Invalid data: {} (path "{}")'.format(
                        e.msg, "".join(str(path) for path in e.path)
                    )
                )
            return f(*args, **kwargs)

        return new_func

    return decorator
