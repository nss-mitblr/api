from sanic import Sanic
from .app import appserver

app: Sanic = appserver

# flake8: noqa
import nss_api.endpoints

if __name__ == "__main__":
    # Use a KWARGS dict to pass to app.run dynamically
    kwargs = {"access_log": True, "host": "0.0.0.0"}

    kwargs["debug"] = True
    kwargs["auto_reload"] = True

    # Run the API Server
    app.run(**kwargs)
