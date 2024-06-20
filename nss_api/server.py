import json

import aiohttp
import jwt
import motor.motor_asyncio as async_motor
from dotenv import dotenv_values
from sanic import Sanic
from sanic.log import logger

from .app import appserver

app: Sanic = appserver

# flake8: noqa
import nss_api.endpoints

logger.debug("Loading ENV")
config = dotenv_values(".env")

# Read the public and private keys and add them to the config.
with open("public-key.pem") as public_key_file:
    config["PUB_KEY"] = public_key_file.read()

with open("private-key.pem") as private_key_file:
    config["PRIV_KEY"] = private_key_file.read()

# Try to get state from the ENV, defaults to being dev.
is_prod: str = config.get("IS_PROD", "false")

# Convert the string to a bool and update the config with the bool.
config.update({"IS_PROD": is_prod.lower() == "true"})

app: Sanic = appserver
app.config.update(config)
app.config.PROXIES_COUNT = int(config.get("PROXIES_COUNT", 0))


@app.listener("before_server_start")
async def setup_app(app: Sanic):
    logger.info("Connecting to MongoDB.")
    connection = app.config.get("MONGO_CONNECTION_URI")

    if connection is None:
        logger.error("Missing MongoDB URL")
        app.stop(terminate=True)

    client = async_motor.AsyncIOMotorClient(
        connection,
        maxIdleTimeMS=10000,
        minPoolSize=10,
        maxPoolSize=50,
        connectTimeoutMS=10000,
        retryWrites=True,
        waitQueueTimeoutMS=10000,
        serverSelectionTimeoutMS=10000,
    )

    logger.info("Connected to MongoDB.")

    # Add MongoDB connection client to ctx for use in other modules.
    app.ctx.db_client = client

    # Check for production environment.
    is_prod = app.config["IS_PROD"]
    if is_prod:
        logger.info("Connected to PRODUCTION")
        app.ctx.db = client["nss-api"]
    else:
        logger.info("Connected to DEV ENV")
        app.ctx.db = client["nss-api-dev"]

    app.ctx.tokens = {}

    logger.info("Fetching OpenID Configuration of Entra")

    # Fetch OpenID Configuration of Entra from https://login.microsoftonline.com/common/.well-known/openid-configuration
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

    logger.info("Saving public keys to the app context")
    app.ctx.public_keys = public_keys

    logger.info("Setup complete.")


if __name__ == "__main__":
    # Use a KWARGS dict to pass to app.run dynamically
    kwargs = {"access_log": True, "host": "0.0.0.0"}

    kwargs["debug"] = not app.config["IS_PROD"]
    kwargs["auto_reload"] = True

    # Run the API Server
    app.run(**kwargs)
