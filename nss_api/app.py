from sanic import Sanic


class NSS_API(Sanic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctx.entra_public_keys = dict()

    def get_entra_jwt_keys(self) -> dict:
        return self.ctx.entra_public_keys

    def set_entra_jwt_keys(self, keys: dict):
        self.ctx.entra_public_keys = keys

    def get_public_key(self) -> str:
        return self.config["PRIV_KEY"]


appserver = NSS_API("nss-api", strict_slashes=False)
