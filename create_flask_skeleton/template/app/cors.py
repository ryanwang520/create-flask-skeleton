from flask import current_app, request

ALLOWED_HEADERS = (
    "Authorization," "Content-Type",
    "If-Match",
    "If-Modified-Since",
    "If-None-Match",
    "If-Unmodified-Since",
    "Range",
    "X-Requested-With",
)
access_control_allow_headers = ", ".join(ALLOWED_HEADERS)


def append_cors_header(response):
    # always add Access-Control-Allow-Origin header
    response.headers.add(
        "Access-Control-Allow-Origin", current_app.config.get("CORS_DOMAIN", "*")
    )

    # allow cookies to be send
    response.headers.add("Access-Control-Allow-Credentials", "true")

    # always add Access-Control-allow-Headers regard of whether
    # Access-Control-Request-Headers is provided to avoid confusion.
    # and safari requires this
    response.headers.add("Access-Control-Allow-Headers", access_control_allow_headers)

    if request.method == "OPTIONS":

        # for cors preflight request
        if request.headers.get("access-control-request-method"):
            # cache preflight for 24 hours, at least on the server side.
            response.headers.add("Access-Control-Max-Age", "86400")

            response.headers.add(
                "Access-Control-Allow-Methods", "POST, GET, OPTIONS, DELETE, PATCH, PUT"
            )
            return response

    else:
        # for actual request but not preflight
        # e.g: response.headers.add('Access-Control-Expose-Headers', '')
        ...
    return response
