"""API endpoints for callbacks from external (MS-Entra) authentication provider."""
import jwt

from sanic import Request, json
from sanic.log import logger
from sanic.views import HTTPMethodView

from nss_api.app import NSS_API


class ExternalAuthCallback(HTTPMethodView):
    async def post(self, request: Request):
        app: NSS_API = request.app
        # Get the token from the request.
        form = request.form
        token = form["id_token"][0]

        # Get the ID of the key used to sign the token.
        kid = jwt.get_unverified_header(token)["kid"]

        # Get the public key to verify the token.
        key = app.get_entra_jwt_keys().get(kid, "")

        try:
            # Decode the token.
            decoded = jwt.decode(
                token,
                key=key,
                algorithms=["RS256"],
                audience=request.app.config["AZURE_AD_CLIENT_ID"],
            )
        except jwt.exceptions.InvalidAudienceError:
            logger.warning("Invalid audience for JWT")
            # Invalid token
            return json(
                {
                    "authenticated": False,
                    "message": "Invalid token",
                },
                status=401,
            )
        except jwt.exceptions.InvalidIssuedAtError:
            logger.warning("JWT issued in future")
            # Invalid token
            return json(
                {
                    "authenticated": False,
                    "message": "Invalid token",
                },
                status=401,
            )
        except jwt.exceptions.ImmatureSignatureError:
            logger.warning("JWT issued in future")
            # Invalid token
            return json(
                {
                    "authenticated": False,
                    "message": "Invalid token",
                },
                status=401,
            )
        except jwt.exceptions.ExpiredSignatureError:
            logger.warning("JWT has expired")
            # Invalid token
            return json(
                {
                    "authenticated": False,
                    "message": "Invalid token",
                },
                status=401,
            )
        except jwt.exceptions.DecodeError:
            logger.warning("JWT decode error")
            # Invalid token
            return json(
                {
                    "authenticated": False,
                    "message": "Invalid token",
                },
                status=401,
            )

        # Get email from decoded token
        email = decoded["email"]

        # Get domain from email
        domain = email.split("@")[1]

        # Hard domain check for student email
        if domain != "learner.manipal.edu":
            # Check for faculty email
            if domain != "manipal.edu":
                # Invalid email
                return json(
                    {
                        "authenticated": False,
                        "message": "Invalid email domain",
                    },
                    status=401,
                )
            # Faculty email found
            # Payload for JWT
            payload = {
                "name": decoded["name"],
                "email": decoded["email"],
                "jwt_type": "faculty",
            }
            # Calculate Validity of JWT
            valitidy = 7 * 24 * 60
            # Generate JWT
            token = await app.generate_jwt(payload, validity=valitidy)
            # Return JWT
            return json(
                {
                    "authenticated": True,
                    "token": token,
                },
                status=200,
            )

        # Covert to interal UUID
        uuid = email.split("@")[0]

        # Get student from database
        collection = request.app.ctx.db["students"]

        student = await collection.find_one({"email": uuid})

        if student is None:
            # Generate a temp JWT for signups
            payload = {
                "email": email,
                "jwt_type": "signup",
            }

            # Generate JWT for signup
            token = await app.generate_jwt(
                request.app,
                payload,
                validity=30,
            )

            # Redirect to signup
            return json(
                {
                    "authenticated": False,
                    "message": "Requires Signup",
                    "token": token,
                }
            )

            # Student not found
            # return json(
            #     {
            #         "authenticated": False,
            #         "message": "Student not found",
            #     },
            #     status=401,
            # )
        else:
            # Student found
            # Generate JWT
            payload = {
                "name": student["name"],
                "email": student["email"],
                "registeration_number": student["registeration_number"],
                "jwt_type": "student",
            }

            # Calculate Validity of JWT
            valitidy = 30 * 24 * 60

            # Generate JWT
            token = await app.generate_jwt(request.app, payload, validity=valitidy)

            # Return JWT
            return json(
                {
                    "authenticated": True,
                    "token": token,
                },
                status=200,
            )
