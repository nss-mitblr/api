from typing import List, Literal, Optional
from sanic.views import HTTPMethodView

from nss_api.utils.jwt import check_request_for_authorization_status


def authorized(
    require_any: List[
        Optional[
            Literal[
                "signup",
                "student",
                "faculty",
                "external",
                "team",
                "admin",
            ]
        ]
    ] = []
):
    if not require_any:
        require_any = []

    def decorator(f):
        async def decorated_function(*args, **kwargs):
            # Check if the first argument is a view or a request
            if isinstance(args[0], HTTPMethodView):
                request = args[1]
            else:
                request = args[0]

            # Check if the request is authorized
            is_jwt_valid = check_request_for_authorization_status(
                request=request, require_any=require_any
            )

            if is_jwt_valid:
                # Call the function if the request is authorized
                response = await f(*args, **kwargs)
                return response
            else:
                # JWT Check function handels the response
                pass

        return decorated_function

    return decorator
