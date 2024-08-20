from sanic import Request, json
from sanic.views import HTTPMethodView

from nss_api.app import NSS_API


class Event_Manage(HTTPMethodView):
    async def post(self, request: Request):
        """Create a new event."""
        app: NSS_API = request.app
        data = request.json
        db_pool = app.get_db_pool()
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO events (event_name, date, start_time, venue, hours) VALUES (%s, %s, %s, %s, %s)",  # noqa: E501
                    (
                        data["event_name"],
                        data["date"],
                        data["start_time"],
                        data["venue"],
                        data["hours"],
                    ),
                )
        return json({"success": True})

    async def delete(self, request: Request):
        """Delete an event."""
        app: NSS_API = request.app
        data = request.json
        db_pool = app.get_db_pool()
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM events WHERE event_id = %s", (data["event_id"],)
                )
        return json({"success": True})

    async def put(self, request: Request):
        """Update an event."""
        app: NSS_API = request.app
        data = request.json
        db_pool = app.get_db_pool()
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Check if event exists
                await cur.execute(
                    "SELECT 1 FROM events WHERE event_id = %s", (data["event_id"],)
                )
                res = await cur.fetchone()
                if not res:
                    return json(
                        {"success": False, "error": "Event does not exist."}, status=404
                    )
                # Update event
                await cur.execute(
                    "UPDATE events SET event_name = %s, date = %s, start_time = %s, venue = %s, hours = %s WHERE event_id = %s",  # noqa: E501
                    (
                        data["event_name"],
                        data["date"],
                        data["start_time"],
                        data["venue"],
                        data["hours"],
                        data["event_id"],
                    ),
                )
        return json({"success": True})
