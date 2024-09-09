from sanic import Request, json
from sanic.views import HTTPMethodView

from nss_api.app import NSS_API


class Event_Register(HTTPMethodView):
    async def post(self, request: Request):
        """Register a student for an event."""
        app: NSS_API = request.app
        data = request.json
        db_pool = app.get_db_pool()
        user_id = app
        async with db_pool.connection() as conn:
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
                # Register student for event.
                await cur.execute(
                    "INSERT INTO Log (event_id, learner_id, hours, reason,type) VALUES (%s, %s, %s, %s, %s)",  # noqa: E501
                    (
                        data["event_id"],
                        user_id,
                        0,
                        "Registered for event.",
                        "event"
                    ),
                )
        return json({"success": True})
