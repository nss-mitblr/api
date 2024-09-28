from sanic import Request, json
from sanic.views import HTTPMethodView

from nss_api.app import NSS_API


class Event_Volunteers(HTTPMethodView):
    async def get(self, request: Request):
        app: NSS_API = request.app
        db_pool = app.get_db_pool()
        event_id = request.args.get("event_id")
        if not event_id:
            return json({"error": "Event ID is required."}, status=400)
        page = request.args.get("page")
        if page:
            offset = 20 * int(page)
        else:
            offset = 0
        # Get user data from the database
        async with db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Check if event exists and fetch its name
                await cur.execute(
                    "SELECT 1 FROM Events WHERE event_id = %s", (event_id,)
                )
                res = await cur.fetchone()
                if not res:
                    return json(
                        {"success": False, "error": "Event does not exist."}, status=404
                    )
                # Fetch volunteers
                await cur.execute(
                    "SELECT learner_id, name, reg_no FROM Registerations NATURAL JOIN Members m NATURAL JOIN Events e WHERE event_id = %s LIMIT 10 OFFSET %s;",  # noqa: E501
                    (event_id, offset),
                )
                data = await cur.fetchall()
                logs = [
                    {
                        "learner_id": log[0],
                        "name": log[1],
                        "reg_no": log[2],
                    }
                    for log in data
                ]
        return json({"data": logs})
