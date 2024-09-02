from sanic import Request, json
from sanic.views import HTTPMethodView

from nss_api.app import NSS_API
from nss_api.models.db.volunteer_hours_log import Volunteer_Log


class My_Hour_Log(HTTPMethodView):
    async def get(self, request: Request):
        app: NSS_API = request.app
        db_pool = app.get_db_pool()
        # Get user ID from the token
        data = app.decode_jwt(request.token)
        user_id = data["email"]
        # Get user data from the database
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM volunteer_hours_log WHERE email = %s;",
                    (user_id,),
                )
                data = await cur.fetchall()
                logs = [Volunteer_Log(log) for log in data]
        return json({"data": [log.to_dict() for log in logs]})

    async def post(self, request: Request):
        """Triggers the server to update the user's hours on the profile."""
        app: NSS_API = request.app
        db_pool = app.get_db_pool()
        # Get user ID from the token
        data = app.decode_jwt(request.token)
        user_id = data["email"]
        # Get user data from the database
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT * FROM volunteer_hours_log WHERE email = %s;",
                    (user_id,),
                )
                data = await cur.fetchall()
                logs = [Volunteer_Log(log) for log in data]
                hours = sum(log.hours for log in logs)
                await cur.execute(
                    "UPDATE users SET hours = %s WHERE email = %s;",
                    (hours, user_id),
                )
        return json({"data": "Hours updated."})
