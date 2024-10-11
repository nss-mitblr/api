from sanic import Request, json
from sanic.views import HTTPMethodView

from nss_api.app import NSS_API
from nss_api.decorators.require_login import require_login
from nss_api.models.db.student import Student
from nss_api.models.internal.jwt_data import JWT_Data


class About_Me(HTTPMethodView):
    @require_login()
    async def get(self, request: Request, jwt_data: JWT_Data):
        app: NSS_API = request.app
        db_pool = app.get_db_pool()
        # Get user ID
        user_id = jwt_data.email
        # Get user data from the database
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM Members WHERE email = %s;",
                    (user_id,),
                )
                user = await cur.fetchone()

        if user is None:
            return json({"error": "User not found"}, status=404)
        return json({"user": Student(user).to_dict()})
