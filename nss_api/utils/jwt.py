from datetime import datetime, timedelta
from typing import List, Literal, Optional

import jwt
from sanic import Request, Sanic

from nss_api.app import appserver as app
from nss_api.models.internal.jwt_status import JWTStatus


async def check_request_for_authorization_status(
    request: Request,
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
    ],
) -> bool:
    """Checks if the given request is containing a basic auth token"""
    if not request.token:
        return False

    # Validate the JWT token
    state = validate_jwt(request.token)

    if state.authenticated is False:
        return request.json({"error": state.message}, status=401)

    options = {
        "verify_signature": True,
        "require": ["exp", "nbf", "iat", "iss", "user_type"],
        "verify_iss": True,
        "verify_exp": True,
        "verify_iat": True,
        "verify_nbf": True,
    }

    try:
        data = jwt.decode(
            request.token,
            key=request.app.config["PUB_KEY"],
            algorithms="RS256",
            options=options,
        )
    except jwt.InvalidTokenError:
        # Generic invalid token
        return request.json(
            {"error": "An error occurred while validating the JWT token"}, status=401
        )

    # Check if we require a specific scope
    if require_any:
        for scope in require_any:
            if data["user_type"] == scope:
                return True
        # If the user does not have the required scope
        return request.json(
            {"error": "User does not have the required scope"}, status=403
        )
    else:
        return True


async def generate_jwt(
    app: Sanic,
    data: dict,
    validity: int,
    target: Literal["signup", "student", "faculty", "external", "team", "admin"],
) -> str:
    """Generates JWT with given data"""
    now = datetime.utcnow()
    expire = now + timedelta(minutes=validity)
    iss = "NSS_MITBLR_API"
    data.update(
        {"exp": expire, "iat": now, "nbf": now, "iss": iss, "user_type": target.lower()}
    )
    return jwt.encode(data, app.config["PRIV_KEY"], algorithm="RS256")


def validate_jwt(token: str) -> JWTStatus:
    try:
        jwt.decode(token, key=app.config["PUB_KEY"], algorithms="RS256")
    except jwt.exceptions.ImmatureSignatureError:
        # Raised when a token’s nbf claim represents a time in the future
        d = JWTStatus(
            authenticated=False, message="JWT Token not allowed to be used at time"
        )

    except jwt.exceptions.InvalidIssuedAtError:
        # Raised when a token’s iat claim is in the future
        d = JWTStatus(authenticated=False, message="JWT Token issued in the future")

    except jwt.exceptions.ExpiredSignatureError:
        # Raised when a token’s exp claim indicates that it has expired
        d = JWTStatus(authenticated=False, message="JWT Token has expired")

    except jwt.exceptions.InvalidTokenError:
        # Generic invalid token
        d = JWTStatus(authenticated=False, message="JWT Token is invalid")
    else:
        # Valid Token
        d = JWTStatus(authenticated=True)

    return d
