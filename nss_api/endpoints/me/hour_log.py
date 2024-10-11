from sanic import Request, json
from sanic.views import HTTPMethodView

from nss_api.app import NSS_API
from nss_api.decorators.require_login import require_login
from nss_api.models.db.volunteer_hours_log import Volunteer_Log
from nss_api.models.internal.jwt_data import JWT_Data


class My_Hour_Log(HTTPMethodView):
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
                    "SELECT * FROM Log WHERE email = %s;",
                    (user_id,),
                )
                data = await cur.fetchall()
                logs = [Volunteer_Log(log) for log in data]
        return json({"data": [log.to_dict() for log in logs]})

    @require_login()
    async def post(self, request: Request, jwt_data: JWT_Data):
        """Triggers the server to update the user's hours on the profile."""
        app: NSS_API = request.app
        db_pool = app.get_db_pool()
        # Get user ID
        user_id = jwt_data.email
        # Get user data from the database
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM Log WHERE email = %s;",
                    (user_id,),
                )
                data = await cur.fetchall()
                logs = [Volunteer_Log(log) for log in data]
                hours = sum(log.hours for log in logs)
                await cur.execute(
                    "UPDATE Members SET hours = %s WHERE email = %s;",
                    (hours, user_id),
                )
        return json({"data": "Hours updated."})
