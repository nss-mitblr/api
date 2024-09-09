from sanic import Request, json
from sanic.views import HTTPMethodView

import random

from nss_api.app import NSS_API


class Event_Manage(HTTPMethodView):
    async def post(self, request: Request):
        """Create a new event with a unique event_id."""
        app: NSS_API = request.app
        data = request.json
        db_pool = app.get_db_pool()

        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                # Function to generate a random 10-digit string ID
                def generate_random_event_id():
                    return str(random.randint(1000000000, 9999999999))

                # Generate a unique event_id
                event_id = generate_random_event_id()
                while True:
                    await cur.execute(
                        "SELECT event_id FROM Events WHERE event_id = %s", (event_id,)
                    )
                    res = await cur.fetchone()
                    if not res:  # If no such event_id exists, break the loop
                        break
                    event_id = generate_random_event_id()  # Generate a new one

                # Insert the event into the database
                await cur.execute(
                    "INSERT INTO Events (event_id, event_name, event_date, event_time, venue, hours) VALUES (%s, %s, %s, %s, %s, %s)",  # noqa: E501
                    (
                        event_id,
                        data["event_name"],
                        data["event_date"],
                        data["event_time"],
                        data["venue"],
                        data["hours"],
                    ),
                )

        return json({"success": True, "event_id": event_id})


    async def delete(self, request: Request):
        """Delete an event."""
        app: NSS_API = request.app
        data = request.json
        db_pool = app.get_db_pool()
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM Events WHERE event_id = %s", (data["event_id"],)
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
                    "SELECT 1 FROM Events WHERE event_id = %s", (data["event_id"],)
                )
                res = await cur.fetchone()
                if not res:
                    return json(
                        {"success": False, "error": "Event does not exist."}, status=404
                    )
                # Update event
                await cur.execute(
                    "UPDATE Events SET event_name = %s, event_date = %s, event_time = %s, venue = %s, hours = %s WHERE event_id = %s",  # noqa: E501
                    (
                        data["event_name"],
                        data["event_date"],
                        data["event_time"],
                        data["venue"],
                        data["hours"],
                        data["event_id"],
                    ),
                )
        return json({"success": True})
