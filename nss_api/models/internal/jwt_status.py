from typing import Optional


class JWTStatus:
    def __init__(self, authenticated: bool, message: Optional[str] = None):
        self.authenticated = authenticated
        self.message = message

    @property
    def is_valid(self) -> bool:
        return self.authenticated

    @property
    def error_message(self) -> str:
        if self.authenticated:
            return "No error"
        if self.message is None:
            return "An error occurred while validating the JWT token"
        return self.message
