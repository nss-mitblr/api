from datetime import datetime, timedelta, timezone
from sanic import Sanic
import jwt

from nss_api.models.internal.jwt_status import JWTStatus


class NSS_API(Sanic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctx.entra_public_keys = dict()

    def get_entra_jwt_keys(self) -> dict:
        return self.ctx.entra_public_keys

    def set_entra_jwt_keys(self, keys: dict):
        self.ctx.entra_public_keys = keys

    def get_public_key(self) -> str:
        return self.config["PRIV_KEY"]

    def decode_jwt(self, jwt_token: str) -> dict:
        return jwt.decode(jwt_token, key=self.config["PUB_KEY"], algorithms="RS256")

    def check_server_jwt(self, jwt_token: str) -> JWTStatus:
        if not jwt_token or jwt_token == "":
            return JWTStatus(authenticated=False, message="JWT Token not provided")
        try:
            self.decode_jwt(jwt_token)
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

    async def generate_jwt(
        self,
        data: dict,
        validity: int,
    ) -> str:
        """Generates JWT with given data"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=validity)

        try:
            # Attempt to get Host from config
            host = self.config["HOST"]
        except KeyError:
            # Unable to get Host from config, Quit app due to required field
            self.stop()

        iss = f"NSS_API_{host}"
        data.update({"exp": expire, "iat": now, "nbf": now, "iss": iss})
        return jwt.encode(data, self.config["PRIV_KEY"], algorithm="RS256")


appserver = NSS_API("nss-api", strict_slashes=False)
