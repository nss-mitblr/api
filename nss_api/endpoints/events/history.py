from sanic import Request, json
from sanic.views import HTTPMethodView

from nss_api.app import NSS_API
from nss_api.models.db.event import Event


class Event_History(HTTPMethodView):
    async def get(self, request: Request):
        app: NSS_API = request.app
        page = request.args.get("page")
        if page:
            offset = 10 * int(page)
        else:
            offset = 0
        db_pool = app.get_db_pool()
        async with db_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"SELECT * FROM events ORDER BY date DESC LIMIT 10 OFFSET {offset}"
                )
                res = await cur.fetchall()
        return json({"events": [Event(e).to_dict() for e in res]})
