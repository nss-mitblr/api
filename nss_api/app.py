from datetime import datetime, timedelta, timezone
import aiohttp
import aiomysql
from sanic import Sanic
from sanic.log import logger
import jwt
import json

from nss_api.models.internal.jwt_status import JWTStatus


class NSS_API(Sanic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctx.entra_public_keys = dict()

    def get_entra_jwt_keys(self) -> dict:
        return self.ctx.entra_public_keys

    async def load_entra_jwks(self):
        # Fetch OpenID Configuration of Entra
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://login.microsoftonline.com/common/.well-known/openid-configuration"
            ) as resp:
                config = await resp.json()
                jwks_uri = config["jwks_uri"]

        logger.info(
            "Fetching JSON Web Key Set (JWKS) from the OpenID Configuration of Entra"
        )

        # Fetch the JSON Web Key Set (JWKS) from the OpenID Configuration of Entra
        async with aiohttp.ClientSession() as session:
            async with session.get(jwks_uri) as resp:
                jwks = await resp.json()

        logger.info("Saving public keys from the JWKS")

        # Create a dictionary of public keys from the JWKS
        public_keys = {}
        for jwk in jwks["keys"]:
            kid = jwk["kid"]
            public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
        self.ctx.entra_public_keys = public_keys

    def get_public_key(self) -> str:
        return self.config["PRIV_KEY"]

    async def connect_db(self):
        pool = await aiomysql.create_pool(
            host=self.config["DB_HOST"],
            port=self.config["DB_PORT"],
            user=self.config["DB_USERNAME"],
            password=self.config["DB_PASSWORD"],
            db=self.config["DB_NAME"],
            autocommit=True,
        )
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 42;")
                (r,) = await cur.fetchone()
        try:
            assert r == 42
        except AssertionError:
            raise Exception("Database connection failed")
        self.ctx.db_pool = pool

    def get_db_pool(self):
        return self.ctx.db_pool

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
