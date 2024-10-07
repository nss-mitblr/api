from sanic import Request, json
from sanic.views import HTTPMethodView
from sanic_ext import validate

from nss_api.app import NSS_API
from nss_api.models.db.event import Event


class Event_Register(HTTPMethodView):
    @validate(json={"event_id": str})
    async def post(self, request: Request):
        """Register a student for an event."""
        app: NSS_API = request.app
        data = request.json
        db_pool = app.get_db_pool()
        user_id = app.decode_jwt(request.token)["email"]
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Check if event exists
                await cur.execute(
                    "SELECT * FROM Events WHERE event_id = %s", (data["event_id"],)
                )
                res = await cur.fetchone()
                if not res:
                    return json(
                        {"success": False, "error": "Event does not exist."}, status=404
                    )
                event = Event(res)
                # Check if event is register-able
                if event.is_closed():
                    return json(
                        {"success": False, "error": "Event is closed."}, status=400
                    )
                else:
                    try:
                        await cur.execute(
                            "INSERT INTO Registerations (event_id, student_id) VALUES (%s, %s)",
                            (data["event_id"], user_id),
                        )
                    except Exception:
                        return json(
                            {
                                "success": False,
                                "error": "You are already registered for this event.",
                            },
                            status=400,
                        )

        return json({"success": True})
