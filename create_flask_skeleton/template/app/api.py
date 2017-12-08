import json
import functools

from voluptuous import Invalid, Schema
from flask import Response, Flask, request

from .cors import append_cors_header


class ApiResult:
    def __init__(self, value, status=200, next_page=None):
        self.value = value
        self.status = status
        self.nex_page = next_page

    def to_response(self):
        return Response(json.dumps(self.value), status=self.status, mimetype='application/json')


class ApiException(Exception):
    code = None
    message = None
    errors = None
    status = 400

    def __init__(self, message, status=None, *, code=None, errors=None):
        self.message = message
        self.status = status or self.status
        self.code = code or self.code
        self.errors = errors or self.errors

    def to_result(self):
        rv = {'message': self.message}
        if self.errors:
            rv['errors'] = self.errors
        if self.code:
            rv['code'] = self.code
        return ApiResult(rv, status=self.status)


def dataschema(schema):
    if isinstance(schema, dict):
        schema = Schema(schema)

    def decorator(f):
        @functools.wraps(f)
        def new_func(*args, **kwargs):
            try:
                kwargs.update(schema(request.get_json()))
            except Invalid as e:
                raise ApiException('Invalid data: {} (path "{}")'.format(e.msg, "".join(e.path)))
            return f(*args, **kwargs)

        return new_func

    return decorator


class ApiFlask(Flask):

    def make_response(self, rv):
        if isinstance(rv, (dict, list)):
            rv = ApiResult(rv)
        if isinstance(rv, ApiResult):
            return rv.to_response()
        response = super().make_response(rv)
        append_cors_header(response)
        return response
