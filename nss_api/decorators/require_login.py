from sanic import Request, response
from sanic.views import HTTPMethodView

from nss_api.app import NSS_API
from nss_api.models.internal.jwt_status import JWTStatus


def require_login(is_api: bool = False):
    def decorator(f):
        async def decorated_function(*args, **kwargs):
            # Check if the first argument is a view or a request
            if isinstance(args[0], HTTPMethodView):
                request: Request = args[1]
            else:
                request: Request = args[0]

            app: NSS_API = request.app

            # Check if the request is authorized
            is_jwt_valid: JWTStatus = app.check_server_jwt(request.token)

            if is_jwt_valid.authenticated:
                # Call the function if the request is authorized
                return await f(*args, **kwargs)
            else:
                if is_api:
                    return response.json({"error": "Unauthorized access"}, status=401)
                else:
                    return response.redirect("/login")

        return decorated_function

    return decorator
