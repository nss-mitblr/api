from datetime import datetime


class JWT_Data:
    def __init__(self, name, email, uuid, jwt_type, exp, iat, nbf, iss) -> None:
        # Make sure none of the values are None
        if None in (name, email, uuid, jwt_type):
            raise ValueError("All values must be provided")
        self.name = name
        self.email = email
        self.uuid = uuid
        self.jwt_type = jwt_type
        self.exp = datetime.fromtimestamp(exp)
        self.iat = datetime.fromtimestamp(iat)
        self.nbf = datetime.fromtimestamp(nbf)
        self.iss = iss

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "uuid": self.uuid,
            "jwt_type": self.jwt_type,
        }

    def is_admin(self) -> bool:
        return self.jwt_type == "admin"

    def is_valid(self) -> bool:
        now = datetime.now()
        return self.nbf < now < self.exp
